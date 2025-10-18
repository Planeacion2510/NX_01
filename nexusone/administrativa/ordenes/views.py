import os
import shutil
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import OrdenTrabajo, DocumentoOrden, Notificacion
from .forms import OrdenTrabajoForm


# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
@login_required(login_url='/login/')
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().prefetch_related("documentos").order_by("-id")

    # Para cada orden, obtener archivos del disco
    for orden in ordenes:
        carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
        if os.path.exists(carpeta_ot):
            orden.archivos_disponibles = os.listdir(carpeta_ot)
        else:
            orden.archivos_disponibles = []

    # Calcular cierres a tiempo y tardíos
    ordenes_cerradas = [ot for ot in ordenes if ot.estado == "cerrada" and ot.fecha_cierre]
    cierres_a_tiempo = sum([1 for ot in ordenes_cerradas if ot.cierre_a_tiempo == True])
    cierres_tardios = sum([1 for ot in ordenes_cerradas if ot.cierre_a_tiempo == False])

    return render(request, "administrativa/ordenes/listar_orden.html", {
        "ordenes": ordenes,
        "cierres_a_tiempo": cierres_a_tiempo,
        "cierres_tardios": cierres_tardios,
    })


# =====================================================
# ➕ CREAR ORDEN
# =====================================================
@login_required(login_url='/login/')
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save()
            
            # ✅ CREAR NOTIFICACIÓN DE NUEVA ORDEN
            # TEMPORALMENTE COMENTADO HASTA QUE SE EJECUTEN LAS MIGRACIONES
            # Notificacion.objects.create(
            #     orden=orden,
            #     tipo='nueva_orden',
            #     mensaje=f"✨ Nueva orden creada: {orden.numero} - {orden.get_proyecto_display()}"
            # )
            
            archivos = request.FILES.getlist("archivos")

            if archivos:
                # Guardar archivos en el disco
                carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
                os.makedirs(carpeta_ot, exist_ok=True)
                
                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                
                messages.success(request, "✅ Orden creada y archivos guardados correctamente.")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivos).")

            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm()

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "title": "Crear Orden de Trabajo",
    })


# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
@login_required(login_url='/login/')
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Obtener archivos del disco
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        archivos_disponibles = os.listdir(carpeta_ot)
    else:
        archivos_disponibles = []

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            orden.save()

            # Subir nuevos archivos
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                os.makedirs(carpeta_ot, exist_ok=True)
                
                for archivo in nuevos_archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                
                messages.success(request, "✅ Nuevos archivos subidos correctamente.")

            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "orden": orden,
        "archivos_disponibles": archivos_disponibles,
        "title": "Editar Orden de Trabajo",
    })


# =====================================================
# ❌ ELIMINAR DOCUMENTO
# =====================================================
@login_required(login_url='/login/')
def eliminar_documento(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    archivo = request.GET.get("archivo")

    if archivo:
        ruta = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/{archivo}")
        if os.path.exists(ruta):
            os.remove(ruta)
            messages.success(request, "🗑️ Archivo eliminado correctamente.")
        else:
            messages.error(request, "⚠️ Archivo no encontrado.")

    return redirect("administrativa:ordenes:editar_orden", pk=orden.id)


# =====================================================
# ❌ ELIMINAR ORDEN Y CARPETA
# =====================================================
@login_required(login_url='/login/')
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Borrar carpeta del disco
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}")
    
    if os.path.exists(carpeta_ot):
        try:
            # Función para manejar archivos de solo lectura
            def handle_remove_readonly(func, path, exc):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(carpeta_ot, onerror=handle_remove_readonly)
            messages.success(request, "🗑️ Carpeta eliminada correctamente.")
        except Exception as e:
            messages.warning(request, f"⚠️ Error al eliminar carpeta: {e}")

    # Borrar registros en DB
    orden.documentos.all().delete()
    orden.delete()
    messages.success(request, "🗑️ Orden eliminada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 🚫 CERRAR ORDEN
# =====================================================
@login_required(login_url='/login/')
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "cerrada"
    orden.fecha_cierre = timezone.now()
    
    # Calcular si el cierre fue a tiempo
    if orden.fecha_envio:
        fecha_cierre_solo_fecha = orden.fecha_cierre.date()
        fecha_envio_solo_fecha = orden.fecha_envio
        
        if fecha_cierre_solo_fecha <= fecha_envio_solo_fecha:
            orden.cierre_a_tiempo = True
            
            # ✅ CREAR NOTIFICACIÓN DE CIERRE A TIEMPO
            # TEMPORALMENTE COMENTADO HASTA QUE SE EJECUTEN LAS MIGRACIONES
            # Notificacion.objects.create(
            #     orden=orden,
            #     tipo='a_tiempo',
            #     mensaje=f"😀 Orden {orden.numero} cerrada A TIEMPO"
            # )
            
            messages.success(request, "✅ Orden cerrada A TIEMPO correctamente. 😀")
        else:
            orden.cierre_a_tiempo = False
            
            # ✅ CREAR NOTIFICACIÓN DE CIERRE TARDÍO
            # TEMPORALMENTE COMENTADO HASTA QUE SE EJECUTEN LAS MIGRACIONES
            # Notificacion.objects.create(
            #     orden=orden,
            #     tipo='tarde',
            #     mensaje=f"😞 Orden {orden.numero} cerrada TARDÍAMENTE"
            # )
            
            messages.warning(request, "⚠️ Orden cerrada TARDÍAMENTE. 😞")
    else:
        orden.cierre_a_tiempo = None
        messages.success(request, "✅ Orden cerrada (sin fecha de envío para comparar).")
    
    orden.save()
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 📂 DESCARGAR ARCHIVO
# =====================================================
@login_required(login_url='/login/')
def descargar_archivo(request, numero_ot, nombre_archivo):
    """Descargar archivo del disco de Render"""
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/{nombre_archivo}")
    
    if os.path.exists(ruta_archivo):
        return FileResponse(
            open(ruta_archivo, 'rb'), 
            as_attachment=True, 
            filename=nombre_archivo
        )
    else:
        raise Http404("Archivo no encontrado")


# =====================================================
# 🔔 SISTEMA DE NOTIFICACIONES
# =====================================================

@login_required(login_url='/login/')
def obtener_notificaciones(request):
    """Obtiene todas las notificaciones no leídas"""
    notificaciones = Notificacion.objects.filter(leida=False).select_related('orden')[:20]
    
    data = {
        'count': notificaciones.count(),
        'notificaciones': [
            {
                'id': n.id,
                'orden_id': n.orden.id,
                'tipo': n.tipo,
                'mensaje': n.mensaje,
                'fecha': timezone.localtime(n.fecha_creacion).strftime('%d/%m/%Y %H:%M')
            }
            for n in notificaciones
        ]
    }
    
    return JsonResponse(data)


@login_required(login_url='/login/')
def marcar_leida(request, notificacion_id):
    """Marca una notificación como leída"""
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id)
        notificacion.leida = True
        notificacion.save()
        return JsonResponse({'success': True})
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


@login_required(login_url='/login/')
def marcar_todas_leidas(request):
    """Marca todas las notificaciones como leídas"""
    Notificacion.objects.filter(leida=False).update(leida=True)
    return JsonResponse({'success': True})