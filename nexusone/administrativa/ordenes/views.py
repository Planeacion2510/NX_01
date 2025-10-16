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

# URL pública de ngrok (opcional)
NGROK_URL = getattr(settings, "NGROK_URL", "").strip()
if NGROK_URL and not NGROK_URL.endswith("/"):
    NGROK_URL += "/"


# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().prefetch_related("documentos").order_by("-id")

    # Contar cierres a tiempo y tardíos
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

            # Carpeta local de la OT
            carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
            os.makedirs(carpeta_ot, exist_ok=True)

            # Guardar archivos en PC o Render
            archivos = request.FILES.getlist("archivos")
            if archivos:
                guardados = []
                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                    guardados.append(archivo.name)

                messages.success(request, f"✅ Orden creada y archivos guardados: {', '.join(guardados)}")
            else:
                messages.success(request, "✅ Orden creada correctamente (sin archivos).")

            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, ⚠️ Corrige los errores del formulario.")
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

    # 1️⃣ Obtener archivos desde la PC
    if os.path.exists(carpeta_ot):
        archivos_pc = os.listdir(carpeta_ot)

    # 2️⃣ Si no hay archivos locales, intentar vía ngrok
    if not archivos_pc and NGROK_URL:
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

            # Subir nuevos archivos a la PC / Render
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                guardados = []
                for archivo in nuevos_archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    os.makedirs(carpeta_ot, exist_ok=True)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                    guardados.append(archivo.name)
                messages.success(request, f"✅ Nuevos archivos subidos: {', '.join(guardados)}")

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

    # Borrar carpeta local
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        shutil.rmtree(carpeta_ot)

    # Borrar carpeta en PC vía ngrok (opcional)
    if NGROK_URL:
        try:
            requests.post(f"{NGROK_URL}administrativa/ordenes/eliminar-orden-local/", data={"numero_ot": orden.numero}, timeout=10)
        except Exception:
            pass

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
    else:
        # Intentar vía ngrok si existe
        if NGROK_URL:
            try:
                r = requests.get(f"{NGROK_URL}Ordenes/{numero_ot}/{nombre_archivo}", timeout=10)
                if r.status_code == 200:
                    from django.http import HttpResponse
                    response = HttpResponse(r.content, content_type="application/octet-stream")
                    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                    return response
                else:
                    raise Http404("Archivo no encontrado")
            except Exception:
                raise Http404("Archivo no encontrado")
        else:
            raise Http404("Archivo no encontrado")
