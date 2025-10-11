import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm


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

            archivos = request.FILES.getlist("archivos")
            if archivos:
                carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
                os.makedirs(carpeta_ot, exist_ok=True)

                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)

                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        archivo=f"Ordenes/{orden.numero}/{archivo.name}"
                    )

                messages.success(request, "✅ Orden creada y archivos guardados correctamente.")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivos adjuntos).")

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
            archivos = request.FILES.getlist("archivos")

            if archivos:
                carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
                os.makedirs(carpeta_ot, exist_ok=True)

                # Eliminar documentos previos
                for doc in orden.documentos.all():
                    if doc.archivo and os.path.exists(doc.archivo.path):
                        os.remove(doc.archivo.path)
                    doc.delete()

                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)

                    DocumentoOrden.objects.create(
                        orden=orden,
                        nombre=archivo.name,
                        archivo=f"Ordenes/{orden.numero}/{archivo.name}"
                    )

                messages.success(request, "✅ Orden actualizada y archivos reemplazados correctamente.")
            else:
                messages.success(request, "✅ Orden actualizada correctamente (sin modificar archivos).")

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

    # Eliminar archivos locales
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        for root, dirs, files in os.walk(carpeta_ot, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(carpeta_ot)

    # Eliminar registros de BD
    orden.documentos.all().delete()
    orden.delete()

    messages.success(request, "🗑️ Orden y archivos eliminados correctamente.")
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
