# nexusone/produccion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone

# Importar modelos
from nexusone.administrativa.ordenes.models import OrdenTrabajo
from .models import (
    AvanceProduccion,
    AsignacionOperario,
    MaterialOrden,
    PausaProduccion
)


# ==================================================
# MENÚ PRINCIPAL PRODUCCIÓN
# ==================================================
@login_required(login_url='/login/')
def menu_produccion(request):
    """Menú principal del módulo de producción"""
    return render(request, 'produccion/menu_produccion.html')


# ==================================================
# DASHBOARD PRODUCCIÓN
# ==================================================
@login_required(login_url='/login/')
def dashboard_produccion(request):
    """Dashboard con indicadores en tiempo real"""
    
    # Órdenes activas
    ots_activas = OrdenTrabajo.objects.filter(
        estado__in=['abierta', 'en_proceso']
    ).count()
    
    # Órdenes completadas hoy
    hoy = timezone.now().date()
    ots_completadas_hoy = OrdenTrabajo.objects.filter(
        estado='cerrada',
        fecha_cierre__date=hoy
    ).count()
    
    # Órdenes atrasadas
    ots_atrasadas = OrdenTrabajo.objects.filter(
        estado__in=['abierta', 'en_proceso'],
        fecha_envio__lt=hoy
    ).count()
    
    # Órdenes en riesgo (próximas 3 días)
    from datetime import timedelta
    fecha_riesgo = hoy + timedelta(days=3)
    ots_en_riesgo = OrdenTrabajo.objects.filter(
        estado__in=['abierta', 'en_proceso'],
        fecha_envio__lte=fecha_riesgo,
        fecha_envio__gte=hoy
    ).count()
    
    # Por proceso
    por_proceso = OrdenTrabajo.objects.filter(
        estado__in=['abierta', 'en_proceso']
    ).values('proceso').annotate(total=Count('id'))
    
    # Últimas OTs
    ultimas_ots = OrdenTrabajo.objects.filter(
        estado__in=['abierta', 'en_proceso', 'pendiente']
    ).order_by('-prioridad', 'fecha_envio')[:10]
    
    context = {
        'ots_activas': ots_activas,
        'ots_completadas_hoy': ots_completadas_hoy,
        'ots_atrasadas': ots_atrasadas,
        'ots_en_riesgo': ots_en_riesgo,
        'por_proceso': por_proceso,
        'ultimas_ots': ultimas_ots,
    }
    
    return render(request, 'produccion/dashboard.html', context)


# ==================================================
# LISTA DE ÓRDENES (Vista Operativa)
# ==================================================
@login_required(login_url='/login/')
def lista_ordenes_produccion(request):
    """Lista de órdenes con filtros para producción"""
    
    # Filtros
    estado = request.GET.get('estado', 'todas')
    proceso = request.GET.get('proceso', '')
    prioridad = request.GET.get('prioridad', '')
    busqueda = request.GET.get('q', '')
    
    # Base queryset
    ordenes = OrdenTrabajo.objects.all()
    
    # Aplicar filtros
    if estado == 'urgentes':
        hoy = timezone.now().date()
        ordenes = ordenes.filter(
            estado__in=['abierta', 'en_proceso'],
            fecha_envio__lt=hoy
        )
    elif estado == 'en_proceso':
        ordenes = ordenes.filter(estado='en_proceso')
    elif estado == 'abiertas':
        ordenes = ordenes.filter(estado='abierta')
    elif estado == 'pendientes':
        ordenes = ordenes.filter(estado='pendiente')
    elif estado != 'todas':
        ordenes = ordenes.filter(estado=estado)
    
    if proceso:
        ordenes = ordenes.filter(proceso=proceso)
    
    if prioridad:
        ordenes = ordenes.filter(prioridad=prioridad)
    
    if busqueda:
        ordenes = ordenes.filter(
            Q(numero__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(proyecto_fk__nombre__icontains=busqueda)
        )
    
    # Ordenar por prioridad y fecha
    ordenes = ordenes.select_related(
        'proyecto_fk',
        'responsable',
        'entrega_programada'
    ).order_by('-prioridad', 'fecha_envio')
    
    context = {
        'ordenes': ordenes,
        'estado_filtro': estado,
        'proceso_filtro': proceso,
        'prioridad_filtro': prioridad,
        'busqueda': busqueda,
    }
    
    return render(request, 'produccion/ordenes/lista_ordenes.html', context)


# ==================================================
# DETALLE DE ORDEN
# ==================================================
@login_required(login_url='/login/')
def detalle_orden(request, pk):
    """Detalle completo de una orden con controles de producción"""
    
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related(
            'proyecto_fk',
            'entrega_programada',
            'item_contratado',
            'responsable',
            'orden_dependiente'
        ),
        pk=pk
    )
    
    # Avances de producción
    avances = orden.avances.select_related('registrado_por').order_by('-fecha_registro')[:10]
    
    # Materiales
    materiales = orden.materiales.select_related('insumo').all()
    
    # Asignaciones
    asignaciones = orden.asignaciones.select_related('operario').filter(activo=True)
    
    # Pausas activas
    pausas_activas = orden.pausas.filter(activa=True).select_related('registrado_por')
    
    context = {
        'orden': orden,
        'avances': avances,
        'materiales': materiales,
        'asignaciones': asignaciones,
        'pausas_activas': pausas_activas,
    }
    
    return render(request, 'produccion/ordenes/detalle_orden.html', context)


# ==================================================
# REGISTRAR AVANCE
# ==================================================
@login_required(login_url='/login/')
def registrar_avance(request, pk):
    """Registrar avance de producción en una OT"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        try:
            cantidad = float(request.POST.get('cantidad_avance', 0))
            observaciones = request.POST.get('observaciones', '')
            
            if cantidad <= 0:
                messages.error(request, '⚠️ La cantidad debe ser mayor a cero')
                return redirect('produccion:detalle_orden', pk=pk)
            
            # Verificar que no exceda la cantidad a producir
            if orden.cantidad_producir:
                if (orden.cantidad_producida + cantidad) > orden.cantidad_producir:
                    messages.error(request, '⚠️ La cantidad excede lo requerido')
                    return redirect('produccion:detalle_orden', pk=pk)
            
            # Crear avance
            AvanceProduccion.objects.create(
                orden=orden,
                cantidad_avance=cantidad,
                registrado_por=request.user,
                observaciones=observaciones
            )
            
            # Cambiar estado si estaba pendiente o abierta
            if orden.estado in ['pendiente', 'abierta']:
                orden.estado = 'en_proceso'
                if not orden.fecha_inicio_real:
                    orden.fecha_inicio_real = timezone.now()
                orden.save()
            
            # Si completó la cantidad, sugerir cerrar
            if orden.cantidad_producir and orden.cantidad_producida >= orden.cantidad_producir:
                messages.success(request, '✅ ¡Cantidad completada! Puedes cerrar la orden.')
            else:
                messages.success(request, f'✅ Avance registrado: +{cantidad}')
            
            return redirect('produccion:detalle_orden', pk=pk)
            
        except Exception as e:
            messages.error(request, f'❌ Error al registrar avance: {str(e)}')
            return redirect('produccion:detalle_orden', pk=pk)
    
    return redirect('produccion:detalle_orden', pk=pk)


# ==================================================
# CAMBIAR ESTADO ORDEN
# ==================================================
@login_required(login_url='/login/')
def cambiar_estado_orden(request, pk):
    """Cambiar estado de una orden"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        # Validar dependencias
        if nuevo_estado == 'en_proceso' and not orden.puede_iniciar:
            messages.error(request, '⚠️ No se puede iniciar. Dependencia no cumplida.')
            return redirect('produccion:detalle_orden', pk=pk)
        
        # Cambiar estado
        orden.estado = nuevo_estado
        
        # Registrar fecha de inicio
        if nuevo_estado == 'en_proceso' and not orden.fecha_inicio_real:
            orden.fecha_inicio_real = timezone.now()
        
        # Cerrar orden
        if nuevo_estado == 'cerrada':
            orden.cerrar()
            messages.success(request, '✅ Orden cerrada correctamente')
        else:
            orden.save()
            messages.success(request, f'✅ Estado cambiado a: {orden.get_estado_display()}')
        
        return redirect('produccion:detalle_orden', pk=pk)
    
    return redirect('produccion:detalle_orden', pk=pk)


# ==================================================
# ASIGNAR OPERARIO
# ==================================================
@login_required(login_url='/login/')
def asignar_operario(request, pk):
    """Asignar operario a una orden"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        from django.contrib.auth.models import User
        operario_id = request.POST.get('operario_id')
        
        try:
            operario = User.objects.get(id=operario_id)
            
            # Verificar si ya está asignado
            if AsignacionOperario.objects.filter(orden=orden, operario=operario, activo=True).exists():
                messages.warning(request, '⚠️ Este operario ya está asignado a esta orden')
            else:
                AsignacionOperario.objects.create(
                    orden=orden,
                    operario=operario
                )
                
                # Actualizar responsable en la OT
                if not orden.responsable:
                    orden.responsable = operario
                    orden.save()
                
                messages.success(request, f'✅ Operario {operario.get_full_name() or operario.username} asignado')
            
        except User.DoesNotExist:
            messages.error(request, '❌ Operario no encontrado')
        
        return redirect('produccion:detalle_orden', pk=pk)
    
    return redirect('produccion:detalle_orden', pk=pk)


# ==================================================
# PAUSAR ORDEN
# ==================================================
@login_required(login_url='/login/')
def pausar_orden(request, pk):
    """Pausar una orden de trabajo"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion', '')
        
        # Crear pausa
        PausaProduccion.objects.create(
            orden=orden,
            motivo=motivo,
            descripcion=descripcion,
            registrado_por=request.user
        )
        
        # Cambiar estado
        orden.estado = 'pausada'
        orden.save()
        
        messages.warning(request, f'⏸️ Orden pausada: {descripcion}')
        return redirect('produccion:detalle_orden', pk=pk)
    
    return redirect('produccion:detalle_orden', pk=pk)


# ==================================================
# REANUDAR ORDEN
# ==================================================
@login_required(login_url='/login/')
def reanudar_orden(request, pk):
    """Reanudar una orden pausada"""
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    # Finalizar pausas activas
    for pausa in orden.pausas.filter(activa=True):
        pausa.finalizar()
    
    # Cambiar estado
    orden.estado = 'en_proceso'
    orden.save()
    
    messages.success(request, '▶️ Orden reanudada')
    return redirect('produccion:detalle_orden', pk=pk)