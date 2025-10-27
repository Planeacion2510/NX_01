from django import forms
from .models import Constructora, Proyecto


# ===================================
# 🏢 FORMULARIO CONSTRUCTORA (corregido)
# ===================================
class ConstructoraForm(forms.ModelForm):
    class Meta:
        model = Constructora
        fields = [
            'nombre',
            'nit',
            'direccion',
            'telefono',
            'email',
            'contacto',
            'activo',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Constructora ABC S.A.S.'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789-0'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle 123 # 45-67, Ciudad'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 311 1234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contacto@constructora.com'
            }),
            'contacto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Persona de contacto o representante'
            }),
            'activo': forms.CheckboxInput(attrs={
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
            'ubicacion',
            'descripcion',
            'estado',
            'estado_financiero',
            'porcentaje_avance',
            'fecha_inicio',
            'fecha_fin_estimada',
            'fecha_fin_real',
            'valor_total',
            'valor_pagado',
            'observaciones',
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
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección del proyecto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del proyecto...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'estado_financiero': forms.Select(attrs={
                'class': 'form-control',
            }),
            'porcentaje_avance': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01',
                'placeholder': '0.00'
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
            'valor_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'valor_pagado': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo constructoras activas en el formulario
        self.fields['constructora'].queryset = Constructora.objects.filter(activo=True)


# ===================================
# 📋 FORMULARIO ITEM CONTRATADO
# ===================================
from django.forms import inlineformset_factory
from .models import ItemContratado


class ItemContratadoForm(forms.ModelForm):
    class Meta:
        model = ItemContratado
        fields = ['item', 'unidad', 'cantidad', 'valor_unitario', 'observaciones']
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Apartamento Tipo A'
            }),
            'unidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: unidad, m², m³'
            }),
            'cantidad': forms.TextInput(attrs={
                'class': 'form-control cantidad-item',
                'placeholder': '0'
            }),
            'valor_unitario': forms.TextInput(attrs={
                'class': 'form-control valor-unitario-item',
                'placeholder': '0'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas adicionales del ítem...'
            }),
        }


# Crear el formset para los ítems contratados
ItemContratadoFormSet = inlineformset_factory(
    Proyecto,
    ItemContratado,
    form=ItemContratadoForm,
    extra=1,
    can_delete=True,
    fields=['item', 'unidad', 'cantidad', 'valor_unitario', 'observaciones']
)
