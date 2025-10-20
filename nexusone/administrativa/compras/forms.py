from django import forms
from django.forms import inlineformset_factory
from .models import Proveedor, OrdenCompra, DetalleOrden


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "nit", "direccion", "telefono", "email", "contacto", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "nit": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contacto": forms.TextInput(attrs={"class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ["proveedor", "fecha_entrega", "descripcion", "estado", "destino", "orden_trabajo"]
        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-select"}),
            "fecha_entrega": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "estado": forms.Select(attrs={"class": "form-select"}),

            # 🔹 Nuevo: destino
            "destino": forms.Select(attrs={"class": "form-select"}),

            # 🔹 Nuevo: orden_trabajo (para jalar proyecto/constructora si aplica)
            "orden_trabajo": forms.Select(attrs={"class": "form-select"}),
        }


class DetalleOrdenForm(forms.ModelForm):
    class Meta:
        model = DetalleOrden
        fields = ["producto", "cantidad", "precio_unitario"]
        widgets = {
            "producto": forms.TextInput(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control"}),
        }


# Formset para manejar múltiples detalles en una Orden
DetalleOrdenFormSet = inlineformset_factory(
    OrdenCompra, DetalleOrden,
    form=DetalleOrdenForm,
    extra=1,            # al menos un producto visible
    can_delete=True     # permite eliminar filas
)
