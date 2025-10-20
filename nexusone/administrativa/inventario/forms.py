from django import forms
from .models import Insumo, Maquinaria, Herramienta, MovimientoKardex

# ==============================
# 📌 INSUMOS
# ==============================
class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = [
            "codigo", "nombre", "descripcion", "unidad", 
            "precio_unitario", "stock_minimo", "stock_maximo",
            "iva", "descuento_proveedor" 
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Código del insumo"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del insumo"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción del insumo"}),
            "unidad": forms.TextInput(attrs={"class": "form-control", "placeholder": "Unidad (kg, litros, unidades)"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "stock_maximo": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "iva": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),  
            "descuento_proveedor": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}),
        }

# ==============================
# 📌 MAQUINARIA
# ==============================
class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ["serial", "nombre", "marca", "fecha_compra", "cantidad", "responsable"]
        widgets = {
            "serial": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de serie"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la maquinaria"}),
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Marca"}),
            "fecha_compra": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Responsable"}),
        }


# ==============================
# 📌 HERRAMIENTAS
# ==============================
class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ["nombre", "descripcion", "cantidad", "responsable"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la herramienta"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "responsable": forms.TextInput(attrs={"class": "form-control", "placeholder": "Responsable"}),
        }


# ==============================
# 📌 KARDEX
# ==============================
class MovimientoKardexForm(forms.ModelForm):
    class Meta:
        model = MovimientoKardex
        fields = ["insumo", "tipo", "cantidad", "observacion", "fecha"]
        widgets = {
            "insumo": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "observacion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observación del movimiento..."}),
            "fecha": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
