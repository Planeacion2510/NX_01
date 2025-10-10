import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm
# ✅ Importar funciones de OneDrive
from nexusone.administrativa.utils.azure_drive import upload_file, delete_file


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

            # Subir archivo a OneDrive (si se adjunta)
            archivo = request.FILES.get("archivo")
            if archivo:
                try:
                    nombre_archivo = f"{orden.numero}_{archivo.name}"
                    ruta_remota = f"Ordenes/{orden.numero}/{nombre_archivo}"

                    # Subir archivo a OneDrive
                    result = upload_file(archivo, ruta_remota)

                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        drive_file_id=result.get("id"),
                        drive_view_url=result.get("@microsoft.graph.downloadUrl", ""),
                        drive_download_url=result.get("@microsoft.graph.downloadUrl", ""),
                    )
                    messages.success(request, "✅ Orden creada y archivo subido correctamente a OneDrive.")
                except Exception as e:
                    messages.error(request, f"⚠️ Error subiendo archivo a OneDrive: {e}")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivo adjunto).")

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
                    # Eliminar el archivo anterior en OneDrive
                    try:
                        delete_file(doc.drive_file_id)
                        doc.delete()
                    except Exception as e:
                        messages.warning(request, f"⚠️ No se pudo eliminar el archivo anterior: {e}")

                try:
                    nombre_archivo = f"{orden.numero}_{archivo.name}"
                    ruta_remota = f"Ordenes/{orden.numero}/{nombre_archivo}"
                    result = upload_file(archivo, ruta_remota)

                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        drive_file_id=result.get("id"),
                        drive_view_url=result.get("@microsoft.graph.downloadUrl", ""),
                        drive_download_url=result.get("@microsoft.graph.downloadUrl", ""),
                    )
                    messages.success(request, "✅ Orden actualizada y archivo reemplazado correctamente en OneDrive.")
                except Exception as e:
                    messages.error(request, f"⚠️ Error subiendo nuevo archivo: {e}")
            else:
                messages.success(request, "✅ Orden actualizada correctamente (sin modificar archivo).")

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

    # Eliminar archivos asociados en OneDrive
    for doc in orden.documentos.all():
        if doc.drive_file_id:
            try:
                delete_file(doc.drive_file_id)
            except Exception as e:
                messages.warning(request, f"⚠️ No se pudo eliminar un archivo en OneDrive: {e}")

    # Eliminar registros asociados en base de datos
    orden.documentos.all().delete()
    orden.delete()

    messages.success(request, "🗑️ Orden eliminada correctamente (archivos también eliminados en OneDrive).")
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
