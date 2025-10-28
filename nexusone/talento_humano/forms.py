from django import forms
from .models import (
    Empleado, Contrato, Vacacion, Permiso,
    ExamenMedico, Capacitacion, Dotacion,
    Reglamento, Memorando, HoraExtra,
    Ausentismo, ExamenPeriodico, LlamadoAtencion
)

# --- EMPLEADO ---
class EmpleadoForm(forms.ModelForm):
    contrato_pdf = forms.FileField(
        label="Contrato (PDF)",
        required=False,
        widget=forms.FileInput(attrs={"accept": "application/pdf"})
    )

    class Meta:
        model = Empleado
        fields = ["user", "documento", "cargo", "area", "fecha_ingreso", "estado", "contrato_pdf"]
        widgets = {
            "fecha_ingreso": forms.DateInput(attrs={"type": "date"}),
        }

# --- CONTRATO ---
class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["empleado", "tipo", "fecha_inicio", "fecha_fin", "salario", "activo", "archivo"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

# --- VACACIONES ---
class VacacionForm(forms.ModelForm):
    class Meta:
        model = Vacacion
        fields = ["empleado", "fecha_inicio", "fecha_fin", "aprobada"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

# --- PERMISOS ---
class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ["empleado", "fecha", "motivo", "aprobado"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

# --- SST ---
class ExamenMedicoForm(forms.ModelForm):
    class Meta:
        model = ExamenMedico
        fields = ["empleado", "tipo", "fecha", "resultado"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

class CapacitacionForm(forms.ModelForm):
    class Meta:
        model = Capacitacion
        fields = ["empleado", "nombre", "fecha", "completado"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

class DotacionForm(forms.ModelForm):
    class Meta:
        model = Dotacion
        fields = ["empleado", "item", "fecha_entrega", "cantidad"]
        widgets = {
            "fecha_entrega": forms.DateInput(attrs={"type": "date"}),
        }

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
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

class AusentismoForm(forms.ModelForm):
    class Meta:
        model = Ausentismo
        fields = ["empleado", "fecha_inicio", "fecha_fin", "motivo", "justificado"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

class ExamenPeriodicoForm(forms.ModelForm):
    class Meta:
        model = ExamenPeriodico
        fields = ["empleado", "tipo", "fecha", "resultado"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

class LlamadoAtencionForm(forms.ModelForm):
    class Meta:
        model = LlamadoAtencion
        fields = ["empleado", "fecha", "motivo", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }
