# nexusone/talento_humano/forms.py
from django import forms
from .models import Empleado, Contrato, Vacacion, Permiso

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["user", "documento", "cargo", "area", "fecha_ingreso", "tipo_contrato", "estado"]

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["empleado", "fecha_inicio", "fecha_fin", "salario", "archivo"]

class VacacionForm(forms.ModelForm):
    class Meta:
        model = Vacacion
        fields = ["empleado", "fecha_inicio", "fecha_fin", "aprobado"]

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ["empleado", "motivo", "aprobado"]
