# -*- coding: utf-8 -*-
from django import forms
from .models import OrdenTrabajo, DocumentoOrden
from django.forms import modelformset_factory


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ["descripcion", "constructora", "proyecto", "proceso", "estado", "fecha_envio"]

        # ✅ AGREGAR LABELS PARA EVITAR PROBLEMAS DE CODIFICACIÓN
        labels = {
            'descripcion': 'Descripción',
            'constructora': 'Constructora',
            'proyecto': 'Proyecto',
            'proceso': 'Proceso',
            'estado': 'Estado',
            'fecha_envio': 'Fecha de Envío',
        }

        widgets = {
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe brevemente la orden de trabajo..."
            }),
            "constructora": forms.Select(attrs={"class": "form-control"}),
            "proyecto": forms.Select(attrs={"class": "form-control"}),
            "proceso": forms.Select(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-control"}),
            "fecha_envio": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }


class DocumentoOrdenForm(forms.ModelForm):
    class Meta:
        model = DocumentoOrden
        fields = ["nombre", "archivo"]

        # ✅ AGREGAR LABELS
        labels = {
            'nombre': 'Nombre del documento',
            'archivo': 'Archivo',
        }

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del documento (opcional)"
            }),
            "archivo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx",
            }),
        }


# ✅ Solo un campo vacío al crear, con opción de eliminar
DocumentoOrdenFormSet = modelformset_factory(
    DocumentoOrden,
    form=DocumentoOrdenForm,
    extra=1,        # solo uno visible al inicio
    can_delete=True
)