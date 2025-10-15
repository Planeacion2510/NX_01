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
                    try:
                        with open(ruta_archivo, "wb+") as destino:
                            for chunk in archivo.chunks():
                                destino.write(chunk)

                        DocumentoOrden.objects.create(
                            orden=orden,
                            nombre=archivo.name,
                            archivo=f"Ordenes/{orden.numero}/{archivo.name}"
                        )
                    except Exception as e:
                        messages.error(request, f"❌ Error al guardar {archivo.name}: {e}")

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

                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    try:
                        with open(ruta_archivo, "wb+") as destino:
                            for chunk in archivo.chunks():
                                destino.write(chunk)

                        DocumentoOrden.objects.create(
                            orden=orden,
                            nombre=archivo.name,
                            archivo=f"Ordenes/{orden.numero}/{archivo.name}"
                        )
                    except Exception as e:
                        messages.error(request, f"❌ Error al guardar {archivo.name}: {e}")

                messages.success(request, "✅ Archivos agregados correctamente.")
            else:
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
# ❌ ELIMINAR DOCUMENTO INDIVIDUAL
# =====================================================
def eliminar_documento(request, pk):
    doc = get_object_or_404(DocumentoOrden, pk=pk)
    orden_id = doc.orden.id

    if doc.archivo and os.path.exists(doc.archivo.path):
        os.remove(doc.archivo.path)

    doc.delete()
    messages.success(request, "🗑️ Documento eliminado correctamente.")
    return HttpResponseRedirect(reverse("administrativa:ordenes:editar_orden", args=[orden_id]))


# =====================================================
# ❌ ELIMINAR ORDEN COMPLETA
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        for root, dirs, files in os.walk(carpeta_ot, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(carpeta_ot)

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
