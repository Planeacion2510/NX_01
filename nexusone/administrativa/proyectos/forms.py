from django import forms
from .models import Constructora, Proyecto


# ===================================
# 🏢 FORMULARIO CONSTRUCTORA
# ===================================
class ConstructoraForm(forms.ModelForm):
    class Meta:
        model = Constructora
        fields = [
            'razon_social',
            'nit',
            'telefono',
            'ubicacion',
            'correo',
            'representante_legal',
            'contacto_adicional',
            'observaciones',
            'activa',
        ]
        widgets = {
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Constructora ABC S.A.S.'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789-0'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 311 1234567'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 123 # 45-67, Ciudad'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contacto@constructora.com'
            }),
            'representante_legal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del representante'
            }),
            'contacto_adicional': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Otros teléfonos, emails o contactos importantes...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas generales sobre la constructora...'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# ===================================
# 🏗️ FORMULARIO PROYECTO
# ===================================
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            'constructora',
            'nombre',
            'codigo',
            'tipo_proyecto',
            'ubicacion_proyecto',
            'contrato',
            'fecha_inicio',
            'fecha_fin_estimada',
            'fecha_fin_real',
            'estado',
            'presupuesto',
            'descripcion',
            'numero_unidades',
            'observaciones',
            'activo',
        ]
        widgets = {
            'constructora': forms.Select(attrs={
                'class': 'form-control',
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Conjunto Residencial Los Cedros'
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PROJ-2025-001'
            }),
            'tipo_proyecto': forms.Select(attrs={
                'class': 'form-control',
            }),
            'ubicacion_proyecto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del proyecto'
            }),
            'contrato': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin_estimada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin_real': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'presupuesto': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del proyecto...'
            }),
            'numero_unidades': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Número de unidades (apartamentos, casas, etc.)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo constructoras activas en el formulario
        self.fields['constructora'].queryset = Constructora.objects.filter(activa=True)