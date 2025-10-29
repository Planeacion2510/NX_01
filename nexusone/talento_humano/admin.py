from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    # Empleados y contratos
    Empleado, Contrato, Certificacion,
    EPS, AFP, ARL, CajaCompensacion,
    
    # Selección
    PerfilCargo, Vacante, Candidato, ProcesoSeleccion,
    
    # Capacitación
    Capacitacion, InscripcionCapacitacion,
    
    # SST
    MatrizRiesgo, ExamenMedico, AccidenteTrabajo, ElementoProteccion, EntregaEPP,
    
    # Bienestar
    ActividadBienestar, EncuestaClimaOrganizacional, RespuestaEncuesta,
    
    # Gestión
    EvaluacionDesempeño, Permiso, Vacacion, Incapacidad, Memorando, ReglamentoInterno
)

# ============================================================================
# CONFIGURACIÓN GLOBAL DEL ADMIN
# ============================================================================

admin.site.site_header = "NEXUSONE ERP - Talento Humano"
admin.site.site_title = "Talento Humano"
admin.site.index_title = "Administración de Talento Humano"


# ============================================================================
# 1. ADMINISTRACIÓN DE PERSONAL
# ============================================================================

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_documento',
        'nombre_completo_link',
        'cargo',
        'area',
        'estado_badge',
        'fecha_ingreso',
        'antiguedad_display',
        'salario_basico',
    ]
    
    list_filter = [
        'estado',
        'area',
        'cargo',
        'fecha_ingreso',
        'genero',
        'eps',
        'afp',
    ]
    
    search_fields = [
        'numero_documento',
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'email_corporativo',
        'cargo',
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'antiguedad_display',
        'get_contrato_actual_display',
    ]
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                ('tipo_documento', 'numero_documento'),
                ('primer_nombre', 'segundo_nombre'),
                ('primer_apellido', 'segundo_apellido'),
                ('fecha_nacimiento', 'lugar_expedicion'),
                ('genero', 'estado_civil'),
                'foto',
            )
        }),
        ('Contacto', {
            'fields': (
                ('celular', 'telefono_fijo'),
                ('email_personal', 'email_corporativo'),
                ('direccion', 'ciudad', 'barrio'),
            )
        }),
        ('Contacto de Emergencia', {
            'fields': (
                'contacto_emergencia_nombre',
                'contacto_emergencia_parentesco',
                'contacto_emergencia_telefono',
            ),
            'classes': ('collapse',),
        }),
        ('Información Laboral', {
            'fields': (
                'fecha_ingreso',
                'antiguedad_display',
                ('cargo', 'area'),
                ('jefe_inmediato', 'sede'),
                'estado',
                'get_contrato_actual_display',
            )
        }),
        ('Salario', {
            'fields': (
                'salario_basico',
                'aplica_auxilio_transporte',
                'salario_integral',
            )
        }),
        ('Seguridad Social', {
            'fields': (
                'eps',
                'afp',
                'arl',
                'caja_compensacion',
            )
        }),
        ('Información Bancaria', {
            'fields': (
                ('banco', 'tipo_cuenta'),
                'numero_cuenta',
            )
        }),
        ('Metadata', {
            'fields': (
                'observaciones',
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def nombre_completo_link(self, obj):
        url = reverse('admin:talento_humano_empleado_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.get_nombre_completo())
    nombre_completo_link.short_description = 'Nombre Completo'
    
    def estado_badge(self, obj):
        colors = {
            'activo': 'green',
            'inactivo': 'red',
            'vacaciones': 'blue',
            'incapacidad': 'orange',
            'suspendido': 'gray',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def antiguedad_display(self, obj):
        antiguedad = obj.get_antiguedad()
        return antiguedad['texto']
    antiguedad_display.short_description = 'Antigüedad'
    
    def get_contrato_actual_display(self, obj):
        contrato = obj.get_contrato_actual()
        if contrato:
            return f"{contrato.get_tipo_display()} - {contrato.numero_contrato}"
        return "Sin contrato activo"
    get_contrato_actual_display.short_description = 'Contrato Actual'
    
    actions = ['activar_empleados', 'inactivar_empleados']
    
    def activar_empleados(self, request, queryset):
        updated = queryset.update(estado='activo')
        self.message_user(request, f'{updated} empleado(s) activado(s).')
    activar_empleados.short_description = 'Activar empleados seleccionados'
    
    def inactivar_empleados(self, request, queryset):
        updated = queryset.update(estado='inactivo')
        self.message_user(request, f'{updated} empleado(s) inactivado(s).')
    inactivar_empleados.short_description = 'Inactivar empleados seleccionados'


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_contrato',
        'empleado',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'dias_restantes',
        'estado_badge',
        'salario',
    ]
    
    list_filter = [
        'tipo',
        'activo',
        'fecha_inicio',
        'fecha_fin',
    ]
    
    search_fields = [
        'numero_contrato',
        'empleado__primer_nombre',
        'empleado__primer_apellido',
        'empleado__numero_documento',
        'cargo',
    ]
    
    readonly_fields = [
        'numero_contrato',
        'fecha_creacion',
        'fecha_actualizacion',
        'creado_por',
        'dias_restantes',
    ]
    
    fieldsets = (
        ('Información del Contrato', {
            'fields': (
                'empleado',
                'numero_contrato',
                'tipo',
                ('fecha_inicio', 'fecha_fin'),
                'dias_restantes',
            )
        }),
        ('Detalles del Cargo', {
            'fields': (
                'cargo',
                'salario',
                'descripcion_funciones',
            )
        }),
        ('Estado', {
            'fields': (
                'activo',
                'archivo',
                'observaciones',
            )
        }),
        ('Metadata', {
            'fields': (
                'creado_por',
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def dias_restantes(self, obj):
        dias = obj.dias_para_vencer()
        if dias is None:
            return "Indefinido"
        elif dias <= 0:
            return format_html('<span style="color: red; font-weight: bold;">VENCIDO</span>')
        elif dias <= 30:
            return format_html('<span style="color: orange; font-weight: bold;">{} días</span>', dias)
        else:
            return f"{dias} días"
    dias_restantes.short_description = 'Días Restantes'
    
    def estado_badge(self, obj):
        if obj.esta_vigente():
            return format_html('<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">VIGENTE</span>')
        else:
            return format_html('<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 3px;">INACTIVO</span>')
    estado_badge.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Certificacion)
class CertificacionAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'tipo',
        'destinatario',
        'fecha_generacion',
        'generado_por',
    ]
    
    list_filter = [
        'tipo',
        'fecha_generacion',
    ]
    
    search_fields = [
        'empleado__primer_nombre',
        'empleado__primer_apellido',
        'destinatario',
    ]
    
    readonly_fields = ['fecha_generacion', 'generado_por']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.generado_por = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# ENTIDADES DE SEGURIDAD SOCIAL
# ============================================================================

@admin.register(EPS)
class EPSAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'codigo', 'porcentaje_aporte', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'nit', 'codigo']


@admin.register(AFP)
class AFPAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'codigo', 'porcentaje_aporte', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'nit', 'codigo']


@admin.register(ARL)
class ARLAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'codigo', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'nit', 'codigo']


@admin.register(CajaCompensacion)
class CajaCompensacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'codigo', 'porcentaje_aporte', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'nit', 'codigo']


# ============================================================================
# 3. SELECCIÓN Y TALENTO
# ============================================================================

@admin.register(PerfilCargo)
class PerfilCargoAdmin(admin.ModelAdmin):
    list_display = ['nombre_cargo', 'area', 'nivel_jerarquico', 'tipo_contrato', 'activo']
    list_filter = ['nivel_jerarquico', 'activo', 'area']
    search_fields = ['nombre_cargo', 'area']


@admin.register(Vacante)
class VacanteAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'perfil_cargo',
        'numero_vacantes',
        'fecha_apertura',
        'fecha_cierre',
        'estado',
        'numero_aplicaciones',
    ]
    
    list_filter = ['estado', 'fecha_apertura']
    search_fields = ['titulo', 'perfil_cargo__nombre_cargo']
    
    def numero_aplicaciones(self, obj):
        return obj.procesos.count()
    numero_aplicaciones.short_description = 'Aplicaciones'


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = [
        'nombres',
        'apellidos',
        'numero_documento',
        'email',
        'celular',
        'años_experiencia',
        'calificacion',
        'fecha_registro',
    ]
    
    list_filter = ['nivel_educacion', 'años_experiencia', 'fecha_registro']
    search_fields = ['nombres', 'apellidos', 'numero_documento', 'email']


@admin.register(ProcesoSeleccion)
class ProcesoSeleccionAdmin(admin.ModelAdmin):
    list_display = [
        'candidato',
        'vacante',
        'etapa_actual',
        'calificacion_entrevista',
        'calificacion_pruebas',
        'fecha_aplicacion',
    ]
    
    list_filter = ['etapa_actual', 'fecha_aplicacion']
    search_fields = ['candidato__nombres', 'candidato__apellidos', 'vacante__titulo']


# ============================================================================
# 4. CAPACITACIÓN
# ============================================================================

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo',
        'fecha_programada',
        'duracion_horas',
        'modalidad',
        'facilitador',
        'inscritos',
        'completada',
    ]
    
    list_filter = ['tipo', 'modalidad', 'completada', 'fecha_programada']
    search_fields = ['nombre', 'facilitador']
    
    def inscritos(self, obj):
        return obj.get_inscritos()
    inscritos.short_description = 'Inscritos'


class InscripcionCapacitacionInline(admin.TabularInline):
    model = InscripcionCapacitacion
    extra = 0
    fields = ['empleado', 'asistio', 'calificacion', 'certificado']


# ============================================================================
# 5. SST
# ============================================================================

@admin.register(MatrizRiesgo)
class MatrizRiesgoAdmin(admin.ModelAdmin):
    list_display = [
        'proceso',
        'actividad',
        'tipo_peligro',
        'nivel_riesgo_badge',
        'responsable',
        'fecha_actualizacion',
    ]
    
    list_filter = ['nivel_riesgo', 'proceso', 'tipo_peligro']
    search_fields = ['proceso', 'actividad', 'peligro_identificado']
    
    def nivel_riesgo_badge(self, obj):
        colors = {
            'bajo': 'green',
            'medio': 'orange',
            'alto': 'red',
            'muy_alto': 'darkred',
        }
        color = colors.get(obj.nivel_riesgo, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_nivel_riesgo_display()
        )
    nivel_riesgo_badge.short_description = 'Nivel de Riesgo'


@admin.register(ExamenMedico)
class ExamenMedicoAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'tipo',
        'fecha',
        'resultado',
        'ips_realizadora',
        'medico_responsable',
    ]
    
    list_filter = ['tipo', 'resultado', 'fecha']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'ips_realizadora']


@admin.register(AccidenteTrabajo)
class AccidenteTrabajoAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'fecha_accidente',
        'lugar',
        'severidad_badge',
        'dias_incapacidad',
        'reportado_arl',
        'investigado_por',
    ]
    
    list_filter = ['severidad', 'reportado_arl', 'fecha_accidente']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'lugar']
    
    def severidad_badge(self, obj):
        colors = {
            'leve': 'green',
            'grave': 'orange',
            'mortal': 'red',
        }
        color = colors.get(obj.severidad, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severidad_display()
        )
    severidad_badge.short_description = 'Severidad'


@admin.register(ElementoProteccion)
class ElementoProteccionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo',
        'stock_actual',
        'stock_minimo',
        'stock_status',
        'vida_util_dias',
        'activo',
    ]
    
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'descripcion']
    
    def stock_status(self, obj):
        if obj.requiere_reposicion():
            return format_html('<span style="color: red; font-weight: bold;">⚠️ BAJO STOCK</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    stock_status.short_description = 'Estado Stock'


@admin.register(EntregaEPP)
class EntregaEPPAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'elemento',
        'cantidad',
        'fecha_entrega',
        'fecha_vencimiento',
        'dias_restantes',
        'entregado_por',
    ]
    
    list_filter = ['fecha_entrega', 'elemento__tipo']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'elemento__nombre']
    
    def dias_restantes(self, obj):
        from datetime import date
        dias = (obj.fecha_vencimiento - date.today()).days
        if dias <= 0:
            return format_html('<span style="color: red;">VENCIDO</span>')
        elif dias <= 30:
            return format_html('<span style="color: orange;">{} días</span>', dias)
        return f"{dias} días"
    dias_restantes.short_description = 'Días Restantes'


# ============================================================================
# 6. BIENESTAR
# ============================================================================

@admin.register(ActividadBienestar)
class ActividadBienestarAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo',
        'fecha_evento',
        'lugar',
        'inscritos',
        'cupo_maximo',
        'costo',
        'completada',
    ]
    
    list_filter = ['tipo', 'completada', 'fecha_evento']
    search_fields = ['nombre', 'lugar']
    
    def inscritos(self, obj):
        return obj.get_inscritos()
    inscritos.short_description = 'Inscritos'


@admin.register(EncuestaClimaOrganizacional)
class EncuestaClimaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo',
        'fecha_inicio',
        'fecha_cierre',
        'activa',
        'anonima',
        'respuestas_count',
    ]
    
    list_filter = ['activa', 'anonima', 'fecha_inicio']
    search_fields = ['titulo', 'descripcion']
    
    def respuestas_count(self, obj):
        return obj.respuestas.count()
    respuestas_count.short_description = 'Respuestas'


@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = [
        'encuesta',
        'empleado',
        'calificacion_general',
        'fecha_respuesta',
    ]
    
    list_filter = ['calificacion_general', 'fecha_respuesta']
    readonly_fields = ['fecha_respuesta']


# ============================================================================
# 7. GESTIÓN
# ============================================================================

@admin.register(EvaluacionDesempeño)
class EvaluacionDesempeñoAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'periodo',
        'fecha_evaluacion',
        'calificacion_promedio',
        'evaluador',
    ]
    
    list_filter = ['periodo', 'fecha_evaluacion']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido']
    readonly_fields = ['calificacion_promedio', 'fecha_creacion']


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'dias',
        'con_goce_sueldo',
        'aprobado_badge',
    ]
    
    list_filter = ['tipo', 'aprobado', 'con_goce_sueldo', 'fecha_solicitud']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'motivo']
    
    def dias(self, obj):
        return obj.get_dias_solicitados()
    dias.short_description = 'Días'
    
    def aprobado_badge(self, obj):
        if obj.aprobado:
            return format_html('<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">APROBADO</span>')
        return format_html('<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">PENDIENTE</span>')
    aprobado_badge.short_description = 'Estado'


@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'fecha_inicio',
        'fecha_fin',
        'dias_habiles',
        'aprobada_badge',
        'aprobada_por',
    ]
    
    list_filter = ['aprobada', 'fecha_solicitud']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido']
    
    def aprobada_badge(self, obj):
        if obj.aprobada:
            return format_html('<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">APROBADA</span>')
        return format_html('<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">PENDIENTE</span>')
    aprobada_badge.short_description = 'Estado'


@admin.register(Incapacidad)
class IncapacidadAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'dias_incapacidad',
        'numero_radicado',
        'entidad_responsable',
    ]
    
    list_filter = ['tipo', 'fecha_inicio']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'numero_radicado']


@admin.register(Memorando)
class MemorandoAdmin(admin.ModelAdmin):
    list_display = [
        'empleado',
        'tipo',
        'asunto',
        'fecha',
        'emitido_por',
    ]
    
    list_filter = ['tipo', 'fecha']
    search_fields = ['empleado__primer_nombre', 'empleado__primer_apellido', 'asunto']


@admin.register(ReglamentoInterno)
class ReglamentoInternoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'version',
        'fecha_vigencia',
        'activo',
        'creado_por',
    ]
    
    list_filter = ['activo', 'fecha_vigencia']
    search_fields = ['nombre', 'version']