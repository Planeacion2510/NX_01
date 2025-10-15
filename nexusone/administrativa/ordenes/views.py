import os
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm

# URL de tu PC vía ngrok (actualizable desde Render)
ngrok_url_actual = "https://unfledged-unsalably-laticia.ngrok-free.dev"


# =====================================================
# 📋 LISTAR
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().order_by("-id")
    cierres_a_tiempo = ordenes.filter(cierre_a_tiempo=True).count()
    cierres_tardios = ordenes.filter(cierre_a_tiempo=False, fecha_cierre__isnull=False).count()
    return render(request, "administrativa/ordenes/listar_orden.html", {
        "ordenes": ordenes,
        "cierres_a_tiempo": cierres_a_tiempo,
        "cierres_tardios": cierres_tardios
    })


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
                endpoint = f"{ngrok_url_actual}/administrativa/ordenes/recibir-archivos-local/"
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

    return render(request, "administrativa/ordenes/form.html", {"form": form, "title": "Crear Orden de Trabajo"})


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
                endpoint = f"{ngrok_url_actual}/administrativa/ordenes/recibir-archivos-local/"
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

    return render(request, "administrativa/ordenes/form.html", {"form": form, "orden": orden, "title": "Editar Orden de Trabajo"})


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

    # 🔹 Eliminar carpeta en tu PC vía ngrok
    try:
        requests.post(f"{ngrok_url_actual}/administrativa/ordenes/eliminar-orden-local/",
                      data={"numero_ot": orden.numero}, timeout=10)
    except Exception as e:
        messages.warning(request, f"No se pudo eliminar la carpeta en la PC: {e}")

    orden.documentos.all().delete()
    orden.delete()
    messages.success(request, "🗑️ Orden y archivos eliminados correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# ✅ CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "cerrada"
    from django.utils import timezone
    orden.fecha_cierre = timezone.now()
    orden.cierre_a_tiempo = True if orden.fecha_cierre <= orden.fecha_envio else False
    orden.save()
    messages.success(request, "✅ Orden cerrada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")
