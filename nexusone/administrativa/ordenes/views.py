import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import OrdenTrabajo
from .forms import OrdenTrabajoForm
from .drive_utils import upload_file, delete_file


# =====================================================
# 📋 LISTAR
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    return render(request, "administrativa/ordenes/listar_orden.html", {"ordenes": ordenes})


# =====================================================
# ➕ CREAR ORDEN
# =====================================================
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES)
        if form.is_valid():
            orden = form.save()

            # Subir archivo si se envió alguno
            archivo = request.FILES.get("archivo")
            if archivo:
                nombre = f"{orden.numero_ot}_{archivo.name}"
                result = upload_file(archivo, nombre)
                orden.archivo_drive_id = result["id"]
                orden.enlace_drive = result["webViewLink"]
                orden.save()

            messages.success(request, "✅ Orden creada y archivo subido correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm()

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "title": "Crear Orden de Trabajo",
    })


# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            orden = form.save()

            # Si se sube un nuevo archivo, reemplazar en Drive
            archivo = request.FILES.get("archivo")
            if archivo:
                if orden.archivo_drive_id:
                    delete_file(orden.archivo_drive_id)

                nombre = f"{orden.numero_ot}_{archivo.name}"
                result = upload_file(archivo, nombre)
                orden.archivo_drive_id = result["id"]
                orden.enlace_drive = result["webViewLink"]
                orden.save()

            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "orden": orden,
        "title": "Editar Orden de Trabajo",
    })


# =====================================================
# ❌ ELIMINAR ORDEN
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Si tiene archivo en Drive, eliminarlo
    if orden.archivo_drive_id:
        delete_file(orden.archivo_drive_id)

    orden.delete()
    messages.success(request, "🗑️ Orden eliminada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 🚫 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "Cerrada"
    orden.save()
    messages.success(request, "✅ Orden cerrada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")

