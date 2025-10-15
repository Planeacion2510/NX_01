import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm


# =====================================================
# 📋 LISTAR
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    return render(request, "administrativa/ordenes/listar.html", {"ordenes": ordenes})


# =====================================================
# 🆕 CREAR
# =====================================================
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save()
            # Guardar documentos adjuntos si los hay
            for file in request.FILES.getlist("documentos"):
                DocumentoOrden.objects.create(orden=orden, archivo=file)
            messages.success(request, "Orden creada correctamente ✅")
            return redirect("lista_ordenes")
        else:
            messages.error(request, "Por favor corrige los errores del formulario ❌")
    else:
        form = OrdenTrabajoForm()

    return render(request, "administrativa/ordenes/form.html", {"form": form})


# =====================================================
# ✏️ EDITAR
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            for file in request.FILES.getlist("documentos"):
                DocumentoOrden.objects.create(orden=orden, archivo=file)
            messages.success(request, "Orden actualizada correctamente ✅")
            return redirect("lista_ordenes")
        else:
            messages.error(request, "Corrige los errores antes de continuar ❌")
    else:
        form = OrdenTrabajoForm(instance=orden)

    documentos = DocumentoOrden.objects.filter(orden=orden)
    return render(
        request,
        "administrativa/ordenes/form.html",
        {"form": form, "documentos": documentos, "orden": orden},
    )


# =====================================================
# ❌ ELIMINAR
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.delete()
    messages.success(request, "Orden eliminada correctamente 🗑️")
    return redirect("lista_ordenes")


# =====================================================
# 🔒 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "Cerrada"  # Asegúrate de que el campo exista en tu modelo
    orden.save()
    messages.success(request, f"La orden #{orden.id} fue cerrada correctamente 🔒")
    return redirect("lista_ordenes")
