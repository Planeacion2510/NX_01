from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Proveedor, OrdenCompra
from .forms import ProveedorForm, OrdenCompraForm, DetalleOrdenFormSet

# =====================================================
# INDEX DE COMPRAS
# =====================================================
def index_compras(request):
    return render(request, "administrativa/compras/index.html")


# =====================================================
# PROVEEDORES
# =====================================================
def lista_proveedores(request):
    """Lista todos los proveedores registrados."""
    proveedores = Proveedor.objects.all()
    return render(
        request,
        "administrativa/compras/proveedores/lista_proveedores.html",
        {"proveedores": proveedores}
    )


def nuevo_proveedor(request):
    """Crea un nuevo proveedor."""
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Proveedor creado correctamente")
            return redirect("administrativa:compras:lista_proveedores")  
    else:
        form = ProveedorForm()
    return render(
        request,
        "administrativa/compras/proveedores/form_proveedor.html",
        {"form": form}
    )


def editar_proveedor(request, pk):
    """Edita un proveedor existente."""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Proveedor actualizado correctamente")
            return redirect("administrativa:compras:lista_proveedores") 
    else:
        form = ProveedorForm(instance=proveedor)
    return render(
        request,
        "administrativa/compras/proveedores/form_proveedor.html",
        {"form": form}
    )


def eliminar_proveedor(request, pk):
    """Elimina un proveedor."""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.delete()
    messages.success(request, "🗑️ Proveedor eliminado correctamente")
    return redirect("administrativa:compras:lista_proveedores")  # corregido


# =====================================================
# ÓRDENES DE COMPRA
# =====================================================
def lista_ordenes(request):
    """Lista todas las órdenes de compra."""
    ordenes = OrdenCompra.objects.all()
    return render(
        request,
        "administrativa/compras/ordenes/lista_ordenes.html",
        {"ordenes": ordenes}
    )


def crear_orden(request):
    """Crea una nueva orden de compra con detalles."""
    if request.method == "POST":
        form = OrdenCompraForm(request.POST)
        formset = DetalleOrdenFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.orden = orden
                detalle.save()
            messages.success(request, "✅ Orden de compra creada correctamente")
            return redirect("administrativa:compras:lista_ordenes")  # corregido
    else:
        form = OrdenCompraForm()
        formset = DetalleOrdenFormSet()
    return render(
        request,
        "administrativa/compras/ordenes/form_orden.html",
        {"form": form, "formset": formset}
    )


def editar_orden(request, pk):
    """Edita una orden de compra existente."""
    orden = get_object_or_404(OrdenCompra, pk=pk)
    if request.method == "POST":
        form = OrdenCompraForm(request.POST, instance=orden)
        formset = DetalleOrdenFormSet(request.POST, instance=orden)
        if form.is_valid() and formset.is_valid():
            orden = form.save()
            formset.save()
            messages.success(request, "✏️ Orden de compra actualizada correctamente")
            return redirect("administrativa:compras:lista_ordenes")  # corregido
    else:
        form = OrdenCompraForm(instance=orden)
        formset = DetalleOrdenFormSet(instance=orden)
    return render(
        request,
        "administrativa/compras/ordenes/form_orden.html",  # usamos mismo template para crear/editar
        {"form": form, "formset": formset}
    )


def eliminar_orden(request, pk):
    """Elimina una orden de compra."""
    orden = get_object_or_404(OrdenCompra, pk=pk)
    orden.delete()
    messages.success(request, "🗑️ Orden de compra eliminada correctamente")
    return redirect("administrativa:compras:lista_ordenes")  # corregido
