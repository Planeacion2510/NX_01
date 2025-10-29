from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Empleado, Contrato, Certificacion, EPS, AFP, ARL, CajaCompensacion,
    PerfilCargo, Vacante, Candidato, ProcesoSeleccion,
    Capacitacion, InscripcionCapacitacion,
    MatrizRiesgo, ExamenMedico, AccidenteTrabajo, ElementoProteccion, EntregaEPP,
    ActividadBienestar, EncuestaClimaOrganizacional, RespuestaEncuesta,
    EvaluacionDesempeño, Permiso, Vacacion, Incapacidad, Memorando, ReglamentoInterno
)

from .forms import (
    EmpleadoForm, EmpleadoBusquedaForm, ContratoForm, RenovarContratoForm, CertificacionForm,
    PerfilCargoForm, VacanteForm, CandidatoForm, ProcesoSeleccionForm,
    CapacitacionForm, InscripcionCapacitacionForm,
    MatrizRiesgoForm, ExamenMedicoForm, AccidenteTrabajoForm, ElementoProteccionForm, EntregaEPPForm,
    ActividadBienestarForm, EncuestaClimaForm, RespuestaEncuestaForm,
    EvaluacionDesempeñoForm, PermisoForm, VacacionForm, IncapacidadForm, MemorandoForm
)

# ============================================================================
# DASHBOARD Y MENÚ PRINCIPAL
# ============================================================================

@login_required
def dashboard_talento_humano(request):
    """Dashboard principal de talento humano"""
    
    # Estadísticas generales
    total_empleados = Empleado.objects.filter(estado='activo').count()
    total_inactivos = Empleado.objects.filter(estado='inactivo').count()
    
    # Contratos por vencer (próximos 30 días)
    fecha_limite = date.today() + timedelta(days=30)
    contratos_por_vencer = Contrato.objects.filter(
        activo=True,
        fecha_fin__lte=fecha_limite,
        fecha_fin__gte=date.today()
    ).count()
    
    # Vacantes abiertas
    vacantes_abiertas = Vacante.objects.filter(estado='abierta').count()
    
    # Capacitaciones programadas (próximo mes)
    capacitaciones_proximas = Capacitacion.objects.filter(
        fecha_programada__gte=date.today(),
        fecha_programada__lte=fecha_limite,
        completada=False
    ).count()
    
    # Alertas SST
    examenes_pendientes = ExamenMedico.objects.filter(
        fecha__lte=date.today() - timedelta(days=365),
        empleado__estado='activo'
    ).count()
    
    # Cumpleaños del mes
    mes_actual = date.today().month
    cumpleañeros = Empleado.objects.filter(
        fecha_nacimiento__month=mes_actual,
        estado='activo'
    ).order_by('fecha_nacimiento__day')[:5]
    
    # Empleados nuevos (últimos 30 días)
    fecha_inicio = date.today() - timedelta(days=30)
    empleados_nuevos = Empleado.objects.filter(
        fecha_ingreso__gte=fecha_inicio
    ).order_by('-fecha_ingreso')[:5]
    
    context = {
        'total_empleados': total_empleados,
        'total_inactivos': total_inactivos,
        'contratos_por_vencer': contratos_por_vencer,
        'vacantes_abiertas': vacantes_abiertas,
        'capacitaciones_proximas': capacitaciones_proximas,
        'examenes_pendientes': examenes_pendientes,
        'cumpleañeros': cumpleañeros,
        'empleados_nuevos': empleados_nuevos,
    }
    
    return render(request, 'talento_humano/dashboard.html', context)


# ============================================================================
# 1. ADMINISTRACIÓN DE PERSONAL - EMPLEADOS
# ============================================================================

class EmpleadoListView(LoginRequiredMixin, ListView):
    """Lista de empleados con búsqueda y filtros"""
    model = Empleado
    template_name = 'talento_humano/empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Empleado.objects.all().select_related('jefe_inmediato', 'eps', 'afp', 'arl')
        
        # Búsqueda
        busqueda = self.request.GET.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(primer_nombre__icontains=busqueda) |
                Q(segundo_nombre__icontains=busqueda) |
                Q(primer_apellido__icontains=busqueda) |
                Q(segundo_apellido__icontains=busqueda) |
                Q(numero_documento__icontains=busqueda) |
                Q(cargo__icontains=busqueda)
            )
        
        # Filtros
        area = self.request.GET.get('area')
        if area:
            queryset = queryset.filter(area=area)
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        cargo = self.request.GET.get('cargo')
        if cargo:
            queryset = queryset.filter(cargo__icontains=cargo)
        
        return queryset.order_by('-fecha_ingreso')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_busqueda'] = EmpleadoBusquedaForm(self.request.GET)
        
        # Obtener áreas únicas para filtro
        context['areas'] = Empleado.objects.values_list('area', flat=True).distinct()
        
        # Estadísticas
        context['total_empleados'] = self.get_queryset().count()
        context['total_activos'] = self.get_queryset().filter(estado='activo').count()
        
        return context


class EmpleadoDetailView(LoginRequiredMixin, DetailView):
    """Detalle completo de empleado"""
    model = Empleado
    template_name = 'talento_humano/empleados/perfil_empleado.html'
    context_object_name = 'empleado'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.object
        
        # Contratos
        context['contratos'] = empleado.contratos.all().order_by('-fecha_inicio')
        context['contrato_actual'] = empleado.get_contrato_actual()
        
        # Capacitaciones
        context['capacitaciones'] = InscripcionCapacitacion.objects.filter(
            empleado=empleado
        ).select_related('capacitacion').order_by('-fecha_inscripcion')[:5]
        
        # Evaluaciones de desempeño
        context['evaluaciones'] = empleado.evaluaciones.all().order_by('-fecha_evaluacion')[:3]
        
        # Permisos y vacaciones
        context['permisos_recientes'] = empleado.permisos.all().order_by('-fecha_solicitud')[:5]
        context['vacaciones_recientes'] = empleado.vacaciones.all().order_by('-fecha_solicitud')[:5]
        
        # SST
        context['examenes_medicos'] = empleado.examenes_medicos.all().order_by('-fecha')[:3]
        context['accidentes'] = empleado.accidentes.all().order_by('-fecha_accidente')[:3]
        
        # Antigüedad
        context['antiguedad'] = empleado.get_antiguedad()
        
        # Días de vacaciones disponibles
        context['dias_vacaciones_disponibles'] = empleado.get_dias_vacaciones_disponibles()
        
        return context


class EmpleadoCreateView(LoginRequiredMixin, CreateView):
    """Crear nuevo empleado"""
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'talento_humano/empleados/form_empleado.html'
    success_url = reverse_lazy('talento_humano:lista_empleados')
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado creado exitosamente.')
        return super().form_valid(form)


class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar empleado"""
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'talento_humano/empleados/form_empleado.html'
    
    def get_success_url(self):
        return reverse_lazy('talento_humano:detalle_empleado', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Empleado actualizado exitosamente.')
        return super().form_valid(form)


@login_required
def inactivar_empleado(request, pk):
    """Inactivar empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        empleado.estado = 'inactivo'
        empleado.save()
        
        # Desactivar contratos activos
        Contrato.objects.filter(empleado=empleado, activo=True).update(activo=False)
        
        messages.success(request, f'Empleado {empleado.get_nombre_completo()} inactivado.')
        return redirect('talento_humano:lista_empleados')
    
    return render(request, 'talento_humano/empleados/confirmar_inactivar.html', {'empleado': empleado})


# ============================================================================
# CONTRATOS
# ============================================================================

class ContratoListView(LoginRequiredMixin, ListView):
    """Lista de contratos"""
    model = Contrato
    template_name = 'talento_humano/contratos/lista_contratos.html'
    context_object_name = 'contratos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Contrato.objects.all().select_related('empleado')
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado == 'vigente':
            queryset = queryset.filter(activo=True)
        elif estado == 'vencido':
            queryset = queryset.filter(fecha_fin__lt=date.today(), activo=True)
        elif estado == 'por_vencer':
            fecha_limite = date.today() + timedelta(days=30)
            queryset = queryset.filter(
                fecha_fin__gte=date.today(),
                fecha_fin__lte=fecha_limite,
                activo=True
            )
        
        return queryset.order_by('-fecha_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Alertas
        fecha_limite = date.today() + timedelta(days=30)
        context['contratos_vencidos'] = Contrato.objects.filter(
            fecha_fin__lt=date.today(),
            activo=True
        ).count()
        
        context['contratos_por_vencer'] = Contrato.objects.filter(
            fecha_fin__gte=date.today(),
            fecha_fin__lte=fecha_limite,
            activo=True
        ).count()
        
        context['contratos_vigentes'] = Contrato.objects.filter(
            activo=True,
            fecha_fin__gte=date.today()
        ).count()
        
        return context


class ContratoCreateView(LoginRequiredMixin, CreateView):
    """Crear nuevo contrato"""
    model = Contrato
    form_class = ContratoForm
    template_name = 'talento_humano/contratos/form_contrato.html'
    success_url = reverse_lazy('talento_humano:lista_contratos')
    
    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Contrato creado exitosamente.')
        return super().form_valid(form)


@login_required
def renovar_contrato(request, pk):
    """Renovar contrato existente"""
    contrato = get_object_or_404(Contrato, pk=pk)
    
    if request.method == 'POST':
        form = RenovarContratoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear nuevo contrato
            tipo_renovacion = form.cleaned_data['tipo_renovacion']
            fecha_inicio = form.cleaned_data['fecha_inicio']
            nuevo_salario = form.cleaned_data['nuevo_salario']
            
            # Calcular fecha fin según tipo
            if tipo_renovacion == 'fijo_1':
                fecha_fin = fecha_inicio + timedelta(days=365)
                tipo_contrato = 'fijo'
            elif tipo_renovacion == 'fijo_6':
                fecha_fin = fecha_inicio + timedelta(days=180)
                tipo_contrato = 'fijo'
            else:  # indefinido
                fecha_fin = None
                tipo_contrato = 'indefinido'
            
            # Crear renovación
            nuevo_contrato = Contrato.objects.create(
                empleado=contrato.empleado,
                tipo=tipo_contrato,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                salario=nuevo_salario,
                cargo=contrato.cargo,
                descripcion_funciones=contrato.descripcion_funciones,
                activo=True,
                creado_por=request.user
            )
            
            # Adjuntar archivo si existe
            if form.cleaned_data.get('archivo_nuevo_contrato'):
                nuevo_contrato.archivo = form.cleaned_data['archivo_nuevo_contrato']
                nuevo_contrato.save()
            
            # Desactivar contrato anterior
            contrato.activo = False
            contrato.save()
            
            # Actualizar salario del empleado
            empleado = contrato.empleado
            empleado.salario_basico = nuevo_salario
            empleado.save()
            
            messages.success(request, f'Contrato renovado exitosamente. Nuevo contrato: {nuevo_contrato.numero_contrato}')
            return redirect('talento_humano:lista_contratos')
    else:
        # Pre-llenar formulario con datos del contrato actual
        initial = {
            'fecha_inicio': contrato.fecha_fin + timedelta(days=1) if contrato.fecha_fin else date.today(),
            'nuevo_salario': contrato.salario,
        }
        form = RenovarContratoForm(initial=initial)
    
    context = {
        'form': form,
        'contrato': contrato,
    }
    
    return render(request, 'talento_humano/contratos/renovar_contrato.html', context)


# ============================================================================
# CERTIFICACIONES
# ============================================================================

@login_required
def generar_certificacion(request, empleado_id=None):
    """Generar certificación laboral"""
    empleado = None
    if empleado_id:
        empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    if request.method == 'POST':
        form = CertificacionForm(request.POST)
        if form.is_valid():
            certificacion = form.save(commit=False)
            certificacion.generado_por = request.user
            certificacion.save()
            
            # Aquí iría la lógica para generar el PDF
            # (Se puede usar ReportLab, WeasyPrint, etc.)
            
            messages.success(request, 'Certificación generada exitosamente.')
            return redirect('talento_humano:detalle_empleado', pk=certificacion.empleado.pk)
    else:
        initial = {}
        if empleado:
            initial['empleado'] = empleado
        form = CertificacionForm(initial=initial)
    
    context = {
        'form': form,
        'empleado': empleado,
    }
    
    return render(request, 'talento_humano/certificaciones/form_certificacion.html', context)


# ============================================================================
# 3. SELECCIÓN Y TALENTO
# ============================================================================

class VacanteListView(LoginRequiredMixin, ListView):
    """Lista de vacantes"""
    model = Vacante
    template_name = 'talento_humano/seleccion/lista_vacantes.html'
    context_object_name = 'vacantes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Vacante.objects.all().select_related('perfil_cargo', 'responsable')
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-fecha_apertura')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacantes_abiertas'] = Vacante.objects.filter(estado='abierta').count()
        context['vacantes_proceso'] = Vacante.objects.filter(estado='en_proceso').count()
        return context


class VacanteDetailView(LoginRequiredMixin, DetailView):
    """Detalle de vacante con kanban de candidatos"""
    model = Vacante
    template_name = 'talento_humano/seleccion/kanban_seleccion.html'
    context_object_name = 'vacante'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacante = self.object
        
        # Organizar candidatos por etapa
        procesos = ProcesoSeleccion.objects.filter(vacante=vacante).select_related('candidato')
        
        context['recibidas'] = procesos.filter(etapa_actual='recibida')
        context['preseleccionados'] = procesos.filter(etapa_actual='preseleccionado')
        context['entrevistas'] = procesos.filter(etapa_actual='entrevista')
        context['pruebas'] = procesos.filter(etapa_actual='pruebas')
        context['referencias'] = procesos.filter(etapa_actual='referencias')
        context['ofertas'] = procesos.filter(etapa_actual='oferta')
        context['contratados'] = procesos.filter(etapa_actual='contratado')
        context['rechazados'] = procesos.filter(etapa_actual='rechazado')
        
        return context


class CandidatoCreateView(LoginRequiredMixin, CreateView):
    """Registrar nuevo candidato"""
    model = Candidato
    form_class = CandidatoForm
    template_name = 'talento_humano/seleccion/form_candidato.html'
    
    def get_success_url(self):
        vacante_id = self.request.GET.get('vacante')
        if vacante_id:
            return reverse_lazy('talento_humano:detalle_vacante', kwargs={'pk': vacante_id})
        return reverse_lazy('talento_humano:lista_vacantes')
    
    def form_valid(self, form):
        candidato = form.save()
        
        # Si viene de una vacante, crear proceso automáticamente
        vacante_id = self.request.GET.get('vacante')
        if vacante_id:
            vacante = get_object_or_404(Vacante, pk=vacante_id)
            ProcesoSeleccion.objects.create(
                vacante=vacante,
                candidato=candidato,
                etapa_actual='recibida'
            )
        
        messages.success(self.request, 'Candidato registrado exitosamente.')
        return super().form_valid(form)


@login_required
def actualizar_etapa_candidato(request, proceso_id):
    """Actualizar etapa de candidato en el proceso de selección"""
    proceso = get_object_or_404(ProcesoSeleccion, pk=proceso_id)
    
    if request.method == 'POST':
        form = ProcesoSeleccionForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etapa actualizada exitosamente.')
            return redirect('talento_humano:detalle_vacante', pk=proceso.vacante.pk)
    else:
        form = ProcesoSeleccionForm(instance=proceso)
    
    context = {
        'form': form,
        'proceso': proceso,
    }
    
    return render(request, 'talento_humano/seleccion/actualizar_etapa.html', context)


# ============================================================================
# 4. CAPACITACIÓN Y DESARROLLO
# ============================================================================

class CapacitacionListView(LoginRequiredMixin, ListView):
    """Lista de capacitaciones"""
    model = Capacitacion
    template_name = 'talento_humano/capacitacion/lista_capacitaciones.html'
    context_object_name = 'capacitaciones'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Capacitacion.objects.all()
        
        # Filtrar por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado == 'proximas':
            queryset = queryset.filter(fecha_programada__gte=date.today(), completada=False)
        elif estado == 'completadas':
            queryset = queryset.filter(completada=True)
        
        return queryset.order_by('-fecha_programada')


class CapacitacionDetailView(LoginRequiredMixin, DetailView):
    """Detalle de capacitación con lista de inscritos"""
    model = Capacitacion
    template_name = 'talento_humano/capacitacion/detalle_capacitacion.html'
    context_object_name = 'capacitacion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        capacitacion = self.object
        
        context['inscritos'] = InscripcionCapacitacion.objects.filter(
            capacitacion=capacitacion
        ).select_related('empleado')
        
        context['cupos_disponibles'] = capacitacion.cupo_maximo - capacitacion.get_inscritos()
        
        return context


@login_required
def inscribir_capacitacion(request, capacitacion_id, empleado_id):
    """Inscribir empleado a capacitación"""
    capacitacion = get_object_or_404(Capacitacion, pk=capacitacion_id)
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # Verificar cupos disponibles
    if capacitacion.get_inscritos() >= capacitacion.cupo_maximo:
        messages.error(request, 'No hay cupos disponibles para esta capacitación.')
        return redirect('talento_humano:detalle_capacitacion', pk=capacitacion_id)
    
    # Verificar si ya está inscrito
    if InscripcionCapacitacion.objects.filter(capacitacion=capacitacion, empleado=empleado).exists():
        messages.warning(request, 'El empleado ya está inscrito en esta capacitación.')
        return redirect('talento_humano:detalle_capacitacion', pk=capacitacion_id)
    
    # Crear inscripción
    InscripcionCapacitacion.objects.create(
        capacitacion=capacitacion,
        empleado=empleado
    )
    
    messages.success(request, f'{empleado.get_nombre_completo()} inscrito exitosamente.')
    return redirect('talento_humano:detalle_capacitacion', pk=capacitacion_id)


# ============================================================================
# 5. SEGURIDAD Y SALUD EN EL TRABAJO
# ============================================================================

@login_required
def dashboard_sst(request):
    """Dashboard de SST"""
    
    # Estadísticas
    total_accidentes = AccidenteTrabajo.objects.filter(
        fecha_accidente__year=date.today().year
    ).count()
    
    examenes_vencidos = ExamenMedico.objects.filter(
        fecha__lte=date.today() - timedelta(days=365),
        empleado__estado='activo'
    ).count()
    
    epp_bajo_stock = ElementoProteccion.objects.filter(
        stock_actual__lte=models.F('stock_minimo'),
        activo=True
    ).count()
    
    # Matriz de riesgos por nivel
    riesgos_alto = MatrizRiesgo.objects.filter(nivel_riesgo='alto').count()
    riesgos_muy_alto = MatrizRiesgo.objects.filter(nivel_riesgo='muy_alto').count()
    
    # Accidentes recientes
    accidentes_recientes = AccidenteTrabajo.objects.all().select_related('empleado').order_by('-fecha_accidente')[:5]
    
    # EPP por entregar próximamente
    fecha_limite = date.today() + timedelta(days=30)
    epp_por_vencer = EntregaEPP.objects.filter(
        fecha_vencimiento__lte=fecha_limite,
        fecha_vencimiento__gte=date.today()
    ).select_related('empleado', 'elemento')[:10]
    
    context = {
        'total_accidentes': total_accidentes,
        'examenes_vencidos': examenes_vencidos,
        'epp_bajo_stock': epp_bajo_stock,
        'riesgos_alto': riesgos_alto,
        'riesgos_muy_alto': riesgos_muy_alto,
        'accidentes_recientes': accidentes_recientes,
        'epp_por_vencer': epp_por_vencer,
    }
    
    return render(request, 'talento_humano/sst/dashboard_sst.html', context)


class MatrizRiesgoListView(LoginRequiredMixin, ListView):
    """Matriz de identificación de riesgos"""
    model = MatrizRiesgo
    template_name = 'talento_humano/sst/matriz_riesgos.html'
    context_object_name = 'riesgos'
    
    def get_queryset(self):
        queryset = MatrizRiesgo.objects.all()
        
        nivel = self.request.GET.get('nivel')
        if nivel:
            queryset = queryset.filter(nivel_riesgo=nivel)
        
        return queryset.order_by('proceso', 'actividad')


class AccidenteTrabajoListView(LoginRequiredMixin, ListView):
    """Lista de accidentes de trabajo"""
    model = AccidenteTrabajo
    template_name = 'talento_humano/sst/lista_accidentes.html'
    context_object_name = 'accidentes'
    paginate_by = 15
    
    def get_queryset(self):
        return AccidenteTrabajo.objects.all().select_related('empleado', 'investigado_por').order_by('-fecha_accidente')


class ElementoProteccionListView(LoginRequiredMixin, ListView):
    """Lista de elementos de protección personal"""
    model = ElementoProteccion
    template_name = 'talento_humano/sst/lista_epp.html'
    context_object_name = 'elementos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['elementos_bajo_stock'] = ElementoProteccion.objects.filter(
            stock_actual__lte=models.F('stock_minimo'),
            activo=True
        )
        return context


# ============================================================================
# 6. BIENESTAR LABORAL
# ============================================================================

class ActividadBienestarListView(LoginRequiredMixin, ListView):
    """Lista de actividades de bienestar"""
    model = ActividadBienestar
    template_name = 'talento_humano/bienestar/lista_actividades.html'
    context_object_name = 'actividades'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = ActividadBienestar.objects.all()
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-fecha_evento')


@login_required
def inscribir_actividad_bienestar(request, actividad_id, empleado_id):
    """Inscribir empleado a actividad de bienestar"""
    actividad = get_object_or_404(ActividadBienestar, pk=actividad_id)
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # Verificar cupos
    if actividad.cupo_maximo and actividad.get_inscritos() >= actividad.cupo_maximo:
        messages.error(request, 'No hay cupos disponibles.')
        return redirect('talento_humano:lista_actividades_bienestar')
    
    # Inscribir
    actividad.empleados_inscritos.add(empleado)
    messages.success(request, f'{empleado.get_nombre_completo()} inscrito en {actividad.nombre}.')
    
    return redirect('talento_humano:lista_actividades_bienestar')


@login_required
def responder_encuesta_clima(request, encuesta_id):
    """Responder encuesta de clima organizacional"""
    encuesta = get_object_or_404(EncuestaClimaOrganizacional, pk=encuesta_id)
    
    # Verificar si la encuesta está activa
    if not encuesta.activa or date.today() > encuesta.fecha_fin:
        messages.error(request, 'Esta encuesta ya no está disponible.')
        return redirect('talento_humano:dashboard')
    
    # Verificar si ya respondió (si no es anónima)
    if not encuesta.anonima:
        empleado = request.user.empleado
        if RespuestaEncuesta.objects.filter(encuesta=encuesta, empleado=empleado).exists():
            messages.warning(request, 'Ya has respondido esta encuesta.')
            return redirect('talento_humano:dashboard')
    
    if request.method == 'POST':
        form = RespuestaEncuestaForm(request.POST)
        if form.is_valid():
            respuesta = form.save(commit=False)
            respuesta.encuesta = encuesta
            
            if not encuesta.anonima:
                respuesta.empleado = request.user.empleado
            
            respuesta.save()
            messages.success(request, 'Gracias por responder la encuesta.')
            return redirect('talento_humano:dashboard')
    else:
        form = RespuestaEncuestaForm()
    
    context = {
        'form': form,
        'encuesta': encuesta,
    }
    
    return render(request, 'talento_humano/bienestar/responder_encuesta.html', context)


# ============================================================================
# 7. GESTIÓN Y RELACIONES LABORALES
# ============================================================================

class PermisoListView(LoginRequiredMixin, ListView):
    """Lista de permisos y licencias"""
    model = Permiso
    template_name = 'talento_humano/gestion/lista_permisos.html'
    context_object_name = 'permisos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Permiso.objects.all().select_related('empleado', 'aprobado_por')
        
        # Filtrar por estado
        estado = self.request.GET.get('estado')
        if estado == 'pendientes':
            queryset = queryset.filter(aprobado=False)
        elif estado == 'aprobados':
            queryset = queryset.filter(aprobado=True)
        
        return queryset.order_by('-fecha_solicitud')


@login_required
def aprobar_permiso(request, pk):
    """Aprobar permiso"""
    permiso = get_object_or_404(Permiso, pk=pk)
    
    permiso.aprobado = True
    permiso.aprobado_por = request.user
    permiso.fecha_aprobacion = timezone.now()
    permiso.save()
    
    messages.success(request, f'Permiso aprobado para {permiso.empleado.get_nombre_completo()}.')
    return redirect('talento_humano:lista_permisos')


class VacacionListView(LoginRequiredMixin, ListView):
    """Lista de vacaciones"""
    model = Vacacion
    template_name = 'talento_humano/gestion/lista_vacaciones.html'
    context_object_name = 'vacaciones'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Vacacion.objects.all().select_related('empleado', 'aprobada_por')
        
        estado = self.request.GET.get('estado')
        if estado == 'pendientes':
            queryset = queryset.filter(aprobada=False)
        elif estado == 'aprobadas':
            queryset = queryset.filter(aprobada=True)
        
        return queryset.order_by('-fecha_solicitud')


class IncapacidadListView(LoginRequiredMixin, ListView):
    """Lista de incapacidades"""
    model = Incapacidad
    template_name = 'talento_humano/gestion/lista_incapacidades.html'
    context_object_name = 'incapacidades'
    paginate_by = 20
    
    def get_queryset(self):
        return Incapacidad.objects.all().select_related('empleado').order_by('-fecha_inicio')


class MemorandoListView(LoginRequiredMixin, ListView):
    """Lista de memorandos y llamados de atención"""
    model = Memorando
    template_name = 'talento_humano/gestion/lista_memorandos.html'
    context_object_name = 'memorandos'
    paginate_by = 20
    
    def get_queryset(self):
        return Memorando.objects.all().select_related('empleado', 'emitido_por').order_by('-fecha')


class EvaluacionDesempeñoListView(LoginRequiredMixin, ListView):
    """Lista de evaluaciones de desempeño"""
    model = EvaluacionDesempeño
    template_name = 'talento_humano/gestion/lista_evaluaciones.html'
    context_object_name = 'evaluaciones'
    paginate_by = 20
    
    def get_queryset(self):
        return EvaluacionDesempeño.objects.all().select_related('empleado', 'evaluador').order_by('-fecha_evaluacion')


# ============================================================================
# VISTAS DE CREACIÓN GENÉRICAS (CBV)
# ============================================================================

class GenericCreateView(LoginRequiredMixin, CreateView):
    """Vista genérica de creación con mensajes"""
    
    def form_valid(self, form):
        messages.success(self.request, f'{self.model._meta.verbose_name} creado exitosamente.')
        return super().form_valid(form)


# Usar para todas las vistas de creación
class ContratoCreateView(GenericCreateView):
    model = Contrato
    form_class = ContratoForm
    template_name = 'talento_humano/contratos/form_contrato.html'
    success_url = reverse_lazy('talento_humano:lista_contratos')


# Continuar con las demás vistas...