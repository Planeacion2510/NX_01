from django import forms
from django.contrib.auth.models import User
from .models import (
    Empleado, Contrato, Certificacion, 
    PerfilCargo, Vacante, Candidato, ProcesoSeleccion,
    Capacitacion, InscripcionCapacitacion,
    MatrizRiesgo, ExamenMedico, AccidenteTrabajo, ElementoProteccion, EntregaEPP,
    ActividadBienestar, EncuestaClimaOrganizacional, RespuestaEncuesta,
    EvaluacionDesempeño, Permiso, Vacacion, Incapacidad, Memorando
)
from datetime import date

# ============================================================================
# FORMULARIOS DE EMPLEADOS
# ============================================================================

class EmpleadoForm(forms.ModelForm):
    """Formulario principal de empleado"""
    
    class Meta:
        model = Empleado
        fields = [
            'tipo_documento', 'numero_documento', 
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'fecha_nacimiento', 'lugar_expedicion', 'genero', 'estado_civil',
            'celular', 'telefono_fijo', 'email_personal', 'email_corporativo',
            'direccion', 'ciudad', 'barrio',
            'contacto_emergencia_nombre', 'contacto_emergencia_parentesco', 'contacto_emergencia_telefono',
            'fecha_ingreso', 'cargo', 'area', 'jefe_inmediato', 'sede', 'estado',
            'salario_basico', 'aplica_auxilio_transporte', 'salario_integral',
            'eps', 'afp', 'arl', 'caja_compensacion',
            'banco', 'tipo_cuenta', 'numero_cuenta',
            'foto', 'observaciones'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567'}),
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Carlos'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gómez'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lugar_expedicion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bogotá D.C.'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '310-123-4567'}),
            'telefono_fijo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '601-234-5678'}),
            'email_personal': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'email_corporativo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@empresa.com'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 45 #12-34'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bogotá D.C.'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kennedy'}),
            'contacto_emergencia_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_emergencia_parentesco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Esposa'}),
            'contacto_emergencia_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '315-987-6543'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operario de Producción'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Producción'}),
            'jefe_inmediato': forms.Select(attrs={'class': 'form-select'}),
            'sede': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Planta Principal'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'salario_basico': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1960000'}),
            'aplica_auxilio_transporte': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salario_integral': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'eps': forms.Select(attrs={'class': 'form-select'}),
            'afp': forms.Select(attrs={'class': 'form-select'}),
            'arl': forms.Select(attrs={'class': 'form-select'}),
            'caja_compensacion': forms.Select(attrs={'class': 'form-select'}),
            'banco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bancolombia'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-select'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234567890'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_salario_basico(self):
        """Validar que el salario no sea menor al SMLV"""
        salario = self.cleaned_data.get('salario_basico')
        SMLV_2025 = 1423500  # Salario mínimo 2025
        
        if salario < SMLV_2025:
            raise forms.ValidationError(f'El salario no puede ser menor al SMLV 2025 (${SMLV_2025:,})')
        
        return salario

    def clean_email_corporativo(self):
        """Generar email corporativo automáticamente si no se proporciona"""
        email = self.cleaned_data.get('email_corporativo')
        if not email:
            primer_nombre = self.cleaned_data.get('primer_nombre', '').lower()
            primer_apellido = self.cleaned_data.get('primer_apellido', '').lower()
            if primer_nombre and primer_apellido:
                email = f"{primer_nombre}.{primer_apellido}@dinnova.com.co"
        return email


class EmpleadoBusquedaForm(forms.Form):
    """Formulario de búsqueda y filtros de empleados"""
    
    busqueda = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, documento, cargo...'
        })
    )
    
    area = forms.ChoiceField(
        required=False,
        choices=[('', 'Todas las áreas')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(Empleado.ESTADO_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    cargo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo'})
    )


# ============================================================================
# FORMULARIOS DE CONTRATOS
# ============================================================================

class ContratoForm(forms.ModelForm):
    """Formulario de contrato laboral"""
    
    class Meta:
        model = Contrato
        fields = [
            'empleado', 'tipo', 'fecha_inicio', 'fecha_fin',
            'salario', 'cargo', 'descripcion_funciones',
            'archivo', 'observaciones', 'activo'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1960000'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operario de Producción'}),
            'descripcion_funciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        # Validar que contratos a término fijo tengan fecha de finalización
        if tipo in ['fijo', 'obra_labor', 'aprendizaje'] and not fecha_fin:
            raise forms.ValidationError('Los contratos a término fijo deben tener fecha de finalización')
        
        # Validar que fecha fin sea mayor a fecha inicio
        fecha_inicio = cleaned_data.get('fecha_inicio')
        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            raise forms.ValidationError('La fecha de finalización debe ser posterior a la fecha de inicio')
        
        return cleaned_data


class RenovarContratoForm(forms.Form):
    """Formulario para renovar contrato"""
    
    tipo_renovacion = forms.ChoiceField(
        label='Tipo de renovación',
        choices=[
            ('fijo_1', 'Término fijo - 1 año'),
            ('fijo_6', 'Término fijo - 6 meses'),
            ('indefinido', 'Convertir a indefinido'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    nuevo_salario = forms.DecimalField(
        label='Nuevo salario',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1960000'})
    )
    
    aplicar_ipc = forms.BooleanField(
        label='Aplicar incremento de IPC',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    archivo_nuevo_contrato = forms.FileField(
        label='Nuevo contrato (PDF)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )


# ============================================================================
# FORMULARIOS DE CERTIFICACIONES
# ============================================================================

class CertificacionForm(forms.ModelForm):
    """Formulario para generar certificaciones"""
    
    class Meta:
        model = Certificacion
        fields = [
            'empleado', 'tipo', 'destinatario',
            'incluir_cargo', 'incluir_fecha_ingreso', 'incluir_tipo_contrato',
            'incluir_salario', 'incluir_funciones', 'incluir_prestaciones',
            'contenido_adicional'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A quien corresponda'}),
            'incluir_cargo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluir_fecha_ingreso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluir_tipo_contrato': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluir_salario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluir_funciones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'incluir_prestaciones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contenido_adicional': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ============================================================================
# FORMULARIOS DE SELECCIÓN
# ============================================================================

class PerfilCargoForm(forms.ModelForm):
    """Formulario de perfil de cargo"""
    
    class Meta:
        model = PerfilCargo
        fields = '__all__'
        widgets = {
            'nombre_cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel_jerarquico': forms.Select(attrs={'class': 'form-select'}),
            'objetivo_cargo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'funciones_principales': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'nivel_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'experiencia_requerida': forms.TextInput(attrs={'class': 'form-control'}),
            'conocimientos_tecnicos': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'competencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'salario_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'salario_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VacanteForm(forms.ModelForm):
    """Formulario de vacante"""
    
    class Meta:
        model = Vacante
        fields = ['perfil_cargo', 'titulo', 'descripcion', 'numero_vacantes', 'fecha_apertura', 'fecha_cierre', 'estado', 'responsable']
        widgets = {
            'perfil_cargo': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Soldador Senior'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'numero_vacantes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_apertura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }


class CandidatoForm(forms.ModelForm):
    """Formulario de candidato"""
    
    class Meta:
        model = Candidato
        fields = [
            'nombres', 'apellidos', 'tipo_documento', 'numero_documento',
            'email', 'celular', 'ciudad',
            'archivo_hv', 'nivel_educacion', 'años_experiencia',
            'observaciones'
        ]
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'archivo_hv': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
            'nivel_educacion': forms.TextInput(attrs={'class': 'form-control'}),
            'años_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProcesoSeleccionForm(forms.ModelForm):
    """Formulario de proceso de selección"""
    
    class Meta:
        model = ProcesoSeleccion
        fields = ['etapa_actual', 'calificacion_entrevista', 'calificacion_pruebas', 'observaciones']
        widgets = {
            'etapa_actual': forms.Select(attrs={'class': 'form-select'}),
            'calificacion_entrevista': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
            'calificacion_pruebas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ============================================================================
# FORMULARIOS DE CAPACITACIÓN
# ============================================================================

class CapacitacionForm(forms.ModelForm):
    """Formulario de capacitación"""
    
    class Meta:
        model = Capacitacion
        fields = [
            'nombre', 'tipo', 'descripcion', 'objetivo',
            'fecha_programada', 'duracion_horas', 'modalidad',
            'facilitador', 'lugar', 'cupo_maximo', 'costo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_programada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duracion_horas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'facilitador': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class InscripcionCapacitacionForm(forms.ModelForm):
    """Formulario de inscripción a capacitación"""
    
    class Meta:
        model = InscripcionCapacitacion
        fields = ['empleado', 'asistio', 'calificacion', 'certificado', 'observaciones']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'asistio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calificacion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5'}),
            'certificado': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# ============================================================================
# FORMULARIOS DE SST
# ============================================================================

class MatrizRiesgoForm(forms.ModelForm):
    """Formulario de matriz de riesgos"""
    
    class Meta:
        model = MatrizRiesgo
        fields = '__all__'
        exclude = ['fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'proceso': forms.TextInput(attrs={'class': 'form-control'}),
            'actividad': forms.TextInput(attrs={'class': 'form-control'}),
            'peligro_identificado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_peligro': forms.TextInput(attrs={'class': 'form-control'}),
            'efectos_posibles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'controles_existentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nivel_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'controles_recomendados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
        }


class ExamenMedicoForm(forms.ModelForm):
    """Formulario de examen médico"""
    
    class Meta:
        model = ExamenMedico
        fields = '__all__'
        exclude = ['fecha_creacion']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Select(attrs={'class': 'form-select'}),
            'ips_realizadora': forms.TextInput(attrs={'class': 'form-control'}),
            'medico_responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class AccidenteTrabajoForm(forms.ModelForm):
    """Formulario de accidente de trabajo"""
    
    class Meta:
        model = AccidenteTrabajo
        fields = '__all__'
        exclude = ['fecha_creacion']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_accidente': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'parte_cuerpo_afectada': forms.TextInput(attrs={'class': 'form-control'}),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
            'causas_inmediatas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'causas_basicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acciones_correctivas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dias_incapacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'reportado_arl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_reporte_arl': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'investigado_por': forms.Select(attrs={'class': 'form-select'}),
            'fecha_investigacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }


class ElementoProteccionForm(forms.ModelForm):
    """Formulario de elemento de protección"""
    
    class Meta:
        model = ElementoProteccion
        fields = '__all__'
        exclude = ['fecha_creacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'vida_util_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EntregaEPPForm(forms.ModelForm):
    """Formulario de entrega de EPP"""
    
    class Meta:
        model = EntregaEPP
        fields = ['empleado', 'elemento', 'cantidad', 'fecha_entrega', 'firma_empleado', 'observaciones']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'elemento': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'firma_empleado': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# ============================================================================
# FORMULARIOS DE BIENESTAR
# ============================================================================

class ActividadBienestarForm(forms.ModelForm):
    """Formulario de actividad de bienestar"""
    
    class Meta:
        model = ActividadBienestar
        fields = '__all__'
        exclude = ['empleados_inscritos', 'fecha_creacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fecha_evento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
            'presupuesto': forms.NumberInput(attrs={'class': 'form-control'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'completada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class EncuestaClimaForm(forms.ModelForm):
    """Formulario de encuesta de clima organizacional"""
    
    class Meta:
        model = EncuestaClimaOrganizacional
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'activa', 'anonima']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'anonima': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RespuestaEncuestaForm(forms.ModelForm):
    """Formulario de respuesta a encuesta"""
    
    class Meta:
        model = RespuestaEncuesta
        fields = [
            'calificacion_general', 'liderazgo', 'comunicacion',
            'trabajo_equipo', 'condiciones_trabajo', 'reconocimiento',
            'desarrollo', 'comentarios', 'sugerencias'
        ]
        widgets = {
            'calificacion_general': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'liderazgo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comunicacion': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'trabajo_equipo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'condiciones_trabajo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'reconocimiento': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'desarrollo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comentarios': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sugerencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ============================================================================
# FORMULARIOS DE GESTIÓN
# ============================================================================

class EvaluacionDesempeñoForm(forms.ModelForm):
    """Formulario de evaluación de desempeño"""
    
    class Meta:
        model = EvaluacionDesempeño
        fields = [
            'empleado', 'periodo', 'fecha_evaluacion',
            'calidad_trabajo', 'productividad', 'conocimiento_tecnico',
            'trabajo_equipo', 'iniciativa', 'puntualidad',
            'fortalezas', 'areas_mejora', 'plan_desarrollo', 'observaciones'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_evaluacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'calidad_trabajo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'productividad': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'conocimiento_tecnico': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'trabajo_equipo': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'iniciativa': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'puntualidad': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'fortalezas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'areas_mejora': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'plan_desarrollo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PermisoForm(forms.ModelForm):
    """Formulario de permiso"""
    
    class Meta:
        model = Permiso
        fields = [
            'empleado', 'tipo', 'fecha_inicio', 'fecha_fin',
            'motivo', 'con_goce_sueldo', 'documento_soporte', 'observaciones'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'con_goce_sueldo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'documento_soporte': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VacacionForm(forms.ModelForm):
    """Formulario de vacaciones"""
    
    class Meta:
        model = Vacacion
        fields = ['empleado', 'fecha_inicio', 'fecha_fin', 'dias_habiles', 'observaciones']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dias_habiles': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class IncapacidadForm(forms.ModelForm):
    """Formulario de incapacidad"""
    
    class Meta:
        model = Incapacidad
        fields = [
            'empleado', 'tipo', 'fecha_inicio', 'fecha_fin', 'dias_incapacidad',
            'numero_radicado', 'entidad_responsable', 'diagnostico',
            'archivo_incapacidad', 'observaciones'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dias_incapacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'numero_radicado': forms.TextInput(attrs={'class': 'form-control'}),
            'entidad_responsable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EPS o ARL'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo_incapacidad': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MemorandoForm(forms.ModelForm):
    """Formulario de memorando"""
    
    class Meta:
        model = Memorando
        fields = ['empleado', 'tipo', 'fecha', 'asunto', 'descripcion_hechos', 'archivo', 'observaciones']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_hechos': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }