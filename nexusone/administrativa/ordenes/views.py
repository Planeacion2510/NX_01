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

NGROK_URL = getattr(settings, "NGROK_URL", "https://unfledged-unsalably-laticia.ngrok-free.dev/")

# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().prefetch_related("documentos").order_by("-id")
    cierres_a_tiempo = sum([1 for ot in ordenes if getattr(ot, "cierre_a_tiempo", False)])
    cierres_tardios = sum([1 for ot in ordenes if getattr(ot, "cierre_a_tiempo", True) is False and ot.fecha_cierre])
    return render(request, "administrativa/ordenes/listar_orden.html", {
        "ordenes": ordenes,
        "cierres_a_tiempo": cierres_a_tiempo,
        "cierres_tardios": cierres_tardios,
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
                    response = requests.post(f"{NGROK_URL}/administrativa/ordenes/recibir-archivos-local/", data=data, files=files, timeout=60)
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
    })

# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    archivos_pc = []

    if os.path.exists(carpeta_ot):
        archivos_pc = os.listdir(carpeta_ot)

    if not archivos_pc and getattr(settings, "NGROK_URL", None):
        try:
            r = requests.get(f"{settings.NGROK_URL}administrativa/ordenes/listar-archivos-local/", params={"numero_ot": orden.numero}, timeout=10)
            if r.status_code == 200:
                archivos_pc = r.json().get("archivos", [])
        except Exception:
            archivos_pc = []

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                files = [("archivos", (a.name, a, a.content_type)) for a in nuevos_archivos]
                data = {"numero_ot": orden.numero}
                endpoint = f"{settings.NGROK_URL}administrativa/ordenes/recibir-archivos-local/"
                try:
                    r = requests.post(endpoint, data=data, files=files, timeout=60)
                    if r.status_code == 200:
                        messages.success(request, "✅ Nuevos archivos subidos correctamente a tu PC.")
                    else:
                        messages.error(request, f"⚠️ Error al subir archivos: {r.text}")
                except Exception as e:
                    messages.error(request, f"❌ No se pudo conectar con tu PC: {e}")
            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:editar_orden", pk=orden.id)
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "orden": orden,
        "archivos_pc": archivos_pc,
        "ngrok_url": getattr(settings, "NGROK_URL", "/media/"),
        "title": f"Editar Orden {orden.numero}",
    })

# =====================================================
# ❌ ELIMINAR DOCUMENTO
# =====================================================
def eliminar_documento(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    archivo = request.GET.get("archivo")
    if archivo:
        ruta = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/{archivo}")
        if os.path.exists(ruta):
            os.remove(ruta)
            messages.success(request, "🗑️ Archivo eliminado correctamente de tu PC.")
        else:
            messages.error(request, "⚠️ Archivo no encontrado en tu PC.")
    return redirect("administrativa:ordenes:editar_orden", pk=orden.id)

# =====================================================
# ❌ ELIMINAR ORDEN Y CARPETA
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        shutil.rmtree(carpeta_ot)
    try:
        requests.post(f"{NGROK_URL}/administrativa/ordenes/eliminar-orden-local/", data={"numero_ot": orden.numero}, timeout=10)
    except Exception as e:
        messages.warning(request, f"No se pudo eliminar carpeta en tu PC: {e}")
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
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/{nombre_archivo}")
    if os.path.exists(ruta_archivo):
        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename=nombre_archivo)
    else:
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
