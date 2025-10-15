import os
import requests
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
                # 🌐 URL de tu túnel ngrok actual (puedes dejarla fija o actualizarla dinámicamente)
                ngrok_url = "https://unfledged-unsalably-laticia.ngrok-free.dev"
                endpoint = f"{ngrok_url}/administrativa/ordenes/recibir-archivos-local/"

                files = [("archivos", (a.name, a, a.content_type)) for a in archivos]
                data = {"numero_ot": orden.numero}

                try:
                    response = requests.post(endpoint, data=data, files=files, timeout=60)
                    if response.status_code == 200:
                        messages.success(request, "✅ Orden creada y archivos guardados en tu PC.")
                    else:
                        messages.error(request, f"⚠️ Error al enviar archivos: {response.text}")
                except Exception as e:
                    messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")
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
                ngrok_url = "https://unfledged-unsalably-laticia.ngrok-free.dev"
                endpoint = f"{ngrok_url}/administrativa/ordenes/recibir-archivos-local/"

                files = [("archivos", (a.name, a, a.content_type)) for a in archivos]
                data = {"numero_ot": orden.numero}

                try:
                    response = requests.post(endpoint, data=data, files=files, timeout=60)
                    if response.status_code == 200:
                        messages.success(request, "✅ Archivos agregados correctamente en tu PC.")
                    else:
                        messages.error(request, f"⚠️ Error al enviar archivos: {response.text}")
                except Exception as e:
                    messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")
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

