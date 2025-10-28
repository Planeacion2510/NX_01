from django import forms
from .models import (
    Empleado, Contrato, Vacacion, Permiso,
    ExamenMedico, Capacitacion, Dotacion,
    Reglamento, Memorando, HoraExtra,
    Ausentismo, ExamenPeriodico, LlamadoAtencion
)

# --- EMPLEADOS, CONTRATOS, VACACIONES, PERMISOS (ya los tienes) ---
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["documento", "cargo", "area", "fecha_ingreso", "estado"]

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["empleado", "tipo", "fecha_inicio", "fecha_fin", "salario", "activo"]

class VacacionForm(forms.ModelForm):
    class Meta:
        model = Vacacion
        fields = ["empleado", "fecha_inicio", "fecha_fin", "aprobada"]

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ["empleado", "fecha", "motivo", "aprobado"]

# --- SST ---
class ExamenMedicoForm(forms.ModelForm):
    class Meta:
        model = ExamenMedico
        fields = ["empleado", "tipo", "fecha", "resultado"]

class CapacitacionForm(forms.ModelForm):
    class Meta:
        model = Capacitacion
        fields = ["empleado", "nombre", "fecha", "completado"]

class DotacionForm(forms.ModelForm):
    class Meta:
        model = Dotacion
        fields = ["empleado", "item", "fecha_entrega", "cantidad"]

# --- DOCUMENTOS ---
class ReglamentoForm(forms.ModelForm):
    class Meta:
        model = Reglamento
        fields = ["nombre", "archivo"]

class MemorandoForm(forms.ModelForm):
    class Meta:
        model = Memorando
        fields = ["empleado", "asunto", "archivo"]

class HoraExtraForm(forms.ModelForm):
    class Meta:
        model = HoraExtra
        fields = ["empleado", "fecha", "horas", "motivo", "aprobado"]

class AusentismoForm(forms.ModelForm):
    class Meta:
        model = Ausentismo
        fields = ["empleado", "fecha_inicio", "fecha_fin", "motivo", "justificado"]

class ExamenPeriodicoForm(forms.ModelForm):
    class Meta:
        model = ExamenPeriodico
        fields = ["empleado", "tipo", "fecha", "resultado"]

class LlamadoAtencionForm(forms.ModelForm):
    class Meta:
        model = LlamadoAtencion
        fields = ["empleado", "fecha", "motivo", "observaciones"]

