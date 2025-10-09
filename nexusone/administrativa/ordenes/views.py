import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OrdenTrabajo, DocumentoOrden
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

            # Subir archivo a Drive (si se adjunta)
            archivo = request.FILES.get("archivo")
            if archivo:
                try:
                    nombre = f"{orden.numero}_{archivo.name}"
                    result = upload_file(archivo, nombre)

                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        drive_file_id=result["id"],
                        drive_view_url=result["webViewLink"],
                        drive_download_url=result["webContentLink"],
                    )
                    messages.success(request, "✅ Orden creada y archivo subido correctamente.")
                except Exception as e:
                    messages.error(request, f"⚠️ Error subiendo archivo a Drive: {e}")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivo).")

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
            archivo = request.FILES.get("archivo")

            if archivo:
                doc = orden.documentos.first()
                if doc and doc.drive_file_id:
                    delete_file(doc.drive_file_id)
                    doc.delete()

                try:
                    nombre = f"{orden.numero}_{archivo.name}"
                    result = upload_file(archivo, nombre)
                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        drive_file_id=result["id"],
                        drive_view_url=result["webViewLink"],
                        drive_download_url=result["webContentLink"],
                    )
                    messages.success(request, "✅ Orden actualizada y archivo reemplazado correctamente.")
                except Exception as e:
                    messages.error(request, f"⚠️ Error al subir nuevo archivo: {e}")
            else:
                messages.success(request, "✅ Orden actualizada correctamente (sin cambiar archivo).")

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

    # Eliminar archivos asociados en Drive
    for doc in orden.documentos.all():
        if doc.drive_file_id:
            delete_file(doc.drive_file_id)

    # Eliminar registros asociados
    orden.documentos.all().delete()
    orden.delete()

    messages.success(request, "🗑️ Orden eliminada correctamente (archivos también eliminados en Drive).")
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 🚫 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "cerrada"
    orden.save()
    messages.success(request, "✅ Orden cerrada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")
