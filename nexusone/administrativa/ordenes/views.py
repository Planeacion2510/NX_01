import os
import shutil
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse, Http404
from django.urls import reverse

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm


NGROK_URL = "https://unfledged-unsalably-laticia.ngrok-free.dev"


# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().prefetch_related("documentos").order_by("-id")

    # Para cada orden, obtener archivos desde la PC vía ngrok
    for orden in ordenes:
        try:
            r = requests.get(
                f"{NGROK_URL}/administrativa/ordenes/listar-archivos-local/",
                params={"numero_ot": orden.numero},
                timeout=5
            )
            if r.status_code == 200:
                orden.archivos_disponibles = r.json().get("archivos", [])
            else:
                orden.archivos_disponibles = []
        except Exception:
            orden.archivos_disponibles = []

    # Calcular cierres a tiempo y tardíos según tus reglas internas
    cierres_a_tiempo = sum([1 for ot in ordenes if getattr(ot, "cierre_a_tiempo", False)])
    cierres_tardios = sum([1 for ot in ordenes if getattr(ot, "cierre_a_tiempo", True) is False and ot.fecha_cierre])

    return render(request, "administrativa/ordenes/listar_orden.html", {
        "ordenes": ordenes,
        "cierres_a_tiempo": cierres_a_tiempo,
        "cierres_tardios": cierres_tardios,
        "ngrok_url": NGROK_URL,
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
                files = [("archivos", (a.name, a, a.content_type)) for a in archivos]
                data = {"numero_ot": orden.numero}
                try:
                    response = requests.post(
                        f"{NGROK_URL}/administrativa/ordenes/recibir-archivos-local/",
                        data=data,
                        files=files,
                        timeout=60
                    )
                    if response.status_code == 200:
                        messages.success(request, "✅ Orden creada y archivos guardados en tu PC.")
                    else:
                        messages.error(request, f"⚠️ Error al enviar archivos: {response.text}")
                except Exception as e:
                    messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivos).")

            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm()

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "title": "Crear Orden de Trabajo",
        "ngrok_url": NGROK_URL,  # ✅ Añadido
    })


# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # 🔍 Intentar obtener archivos desde tu PC vía ngrok
    archivos_pc = []
    try:
        r = requests.get(
            f"{NGROK_URL}/administrativa/ordenes/listar-archivos-local/",
            params={"numero_ot": orden.numero},
            timeout=10
        )
        if r.status_code == 200:
            archivos_pc = r.json().get("archivos", [])
    except Exception as e:
        print(f"Error al obtener archivos desde PC: {e}")

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            orden.save()

            # Subir nuevos archivos a tu PC
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                files = [("archivos", (a.name, a, a.content_type)) for a in nuevos_archivos]
                data = {"numero_ot": orden.numero}
                endpoint = f"{NGROK_URL}/administrativa/ordenes/recibir-archivos-local/"

                try:
                    r = requests.post(endpoint, data=data, files=files, timeout=60)
                    if r.status_code == 200:
                        messages.success(request, "✅ Nuevos archivos subidos correctamente a tu PC.")
                    else:
                        messages.error(request, f"⚠️ Error al subir archivos: {r.text}")
                except Exception as e:
                    messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")

            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "orden": orden,
        "archivos_pc": archivos_pc,
        "ngrok_url": NGROK_URL,
        "title": "Editar Orden de Trabajo",
    })


# =====================================================
# ❌ ELIMINAR DOCUMENTO
# =====================================================
def eliminar_documento(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    archivo = request.GET.get("archivo")

    if archivo:
        # Intentar eliminar desde tu PC vía ngrok
        try:
            r = requests.post(
                f"{NGROK_URL}/administrativa/ordenes/eliminar-archivo-local/",
                data={"numero_ot": orden.numero, "archivo": archivo},
                timeout=10
            )
            if r.status_code == 200:
                messages.success(request, "🗑️ Archivo eliminado correctamente de tu PC.")
            else:
                messages.error(request, "⚠️ Error al eliminar archivo en tu PC.")
        except Exception as e:
            messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")

    return redirect("administrativa:ordenes:editar_orden", pk=orden.id)


# =====================================================
# ❌ ELIMINAR ORDEN Y CARPETA
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Borrar carpeta en tu PC vía ngrok
    try:
        requests.post(
            f"{NGROK_URL}/administrativa/ordenes/eliminar-orden-local/",
            data={"numero_ot": orden.numero},
            timeout=10
        )
    except Exception as e:
        messages.warning(request, f"No se pudo eliminar carpeta en tu PC: {e}")

    # Borrar registros en DB
    orden.documentos.all().delete()
    orden.delete()
    messages.success(request, "🗑️ Orden y carpeta eliminadas correctamente.")
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


# =====================================================
# 📂 DESCARGAR ARCHIVO
# =====================================================
def descargar_archivo_render(request, numero_ot, nombre_archivo):
    try:
        r = requests.get(f"{NGROK_URL}/Ordenes/{numero_ot}/{nombre_archivo}")
        if r.status_code == 200:
            from django.http import HttpResponse
            response = HttpResponse(r.content, content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
        else:
            raise Http404("Archivo no encontrado")
    except Exception:
        raise Http404("Archivo no encontrado")