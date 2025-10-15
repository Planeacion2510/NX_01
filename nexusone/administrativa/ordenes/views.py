import os
import shutil
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm


# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    return render(request, "administrativa/ordenes/listar.html", {"ordenes": ordenes})


# =====================================================
# ➕ CREAR ORDEN
# =====================================================
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save()
            # Guardar documentos subidos
            for file in request.FILES.getlist("documentos"):
                DocumentoOrden.objects.create(orden=orden, archivo=file)
            messages.success(request, "✅ Orden creada correctamente.")
            return redirect("lista_ordenes")
    else:
        form = OrdenTrabajoForm()
    return render(request, "administrativa/ordenes/form.html", {"form": form})


# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            # Agregar nuevos documentos
            for file in request.FILES.getlist("documentos"):
                DocumentoOrden.objects.create(orden=orden, archivo=file)
            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("lista_ordenes")
    else:
        form = OrdenTrabajoForm(instance=orden)

    documentos = DocumentoOrden.objects.filter(orden=orden)
    return render(
        request,
        "administrativa/ordenes/form.html",
        {"form": form, "orden": orden, "documentos": documentos},
    )


# =====================================================
# 🗑️ ELIMINAR ORDEN (CARPETA + ARCHIVOS)
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Ruta de la carpeta en el sistema local
    carpeta_orden = os.path.join(settings.MEDIA_ROOT, f"ordenes/{orden.id}")

    if os.path.exists(carpeta_orden):
        shutil.rmtree(carpeta_orden)  # ❌ elimina carpeta y todo su contenido

    orden.delete()
    messages.success(request, "🗑️ Orden y su carpeta eliminadas correctamente.")
    return redirect("lista_ordenes")


# =====================================================
# 🗑️ ELIMINAR DOCUMENTO INDIVIDUAL (desde form)
# =====================================================
def eliminar_documento(request, pk):
    documento = get_object_or_404(DocumentoOrden, pk=pk)
    orden_id = documento.orden.id

    # Eliminar archivo físico
    if documento.archivo and os.path.exists(documento.archivo.path):
        os.remove(documento.archivo.path)

    documento.delete()
    messages.success(request, "📄 Documento eliminado correctamente.")
    return redirect(reverse("editar_orden", args=[orden_id]))
