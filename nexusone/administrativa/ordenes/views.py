import os
import shutil
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.urls import reverse

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm

# URL de ngrok, tomada de settings
NGROK_URL = getattr(settings, "NGROK_URL", "").rstrip("/") + "/" if getattr(settings, "NGROK_URL", "") else None

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
                carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
                os.makedirs(carpeta_ot, exist_ok=True)
                guardados = []
                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                    guardados.append(archivo.name)
                messages.success(request, f"✅ Orden creada y archivos guardados en tu PC: {', '.join(guardados)}")
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

    # Carpeta local de la OT
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    archivos_pc = []
    if os.path.exists(carpeta_ot):
        archivos_pc = os.listdir(carpeta_ot)
    elif NGROK_URL:
        # Intentar vía ngrok si no hay archivos locales
        try:
            r = requests.get(f"{NGROK_URL}administrativa/ordenes/listar-archivos-local/", params={"numero_ot": orden.numero}, timeout=10)
            if r.status_code == 200:
                archivos_pc = r.json().get("archivos", [])
        except Exception:
            archivos_pc = []

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            form.save()
            # Subir nuevos archivos a la PC
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                os.makedirs(carpeta_ot, exist_ok=True)
                guardados = []
                for archivo in nuevos_archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                    guardados.append(archivo.name)
                messages.success(request, f"✅ Nuevos archivos subidos correctamente: {', '.join(guardados)}")
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
        "ngrok_url": NGROK_URL or "/media/",
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
def descargar_archivo(request, numero_ot, nombre_archivo):
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/{nombre_archivo}")
    if os.path.exists(ruta_archivo):
        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename=nombre_archivo)
    elif NGROK_URL:
        try:
            r = requests.get(f"{NGROK_URL}Ordenes/{numero_ot}/{nombre_archivo}", timeout=10)
            if r.status_code == 200:
                resp = HttpResponse(r.content, content_type="application/octet-stream")
                resp['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                return resp
        except Exception:
            pass
    raise Http404("Archivo no encontrado")
