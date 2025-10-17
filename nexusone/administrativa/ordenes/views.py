import os
import shutil
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse, Http404

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm


# =====================================================
# 📋 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes = OrdenTrabajo.objects.all().prefetch_related("documentos").order_by("-id")

    # Para cada orden, obtener archivos del disco
    for orden in ordenes:
        carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
        if os.path.exists(carpeta_ot):
            orden.archivos_disponibles = os.listdir(carpeta_ot)
        else:
            orden.archivos_disponibles = []

    # Calcular cierres a tiempo y tardíos
    ordenes_cerradas = [ot for ot in ordenes if ot.estado == "cerrada" and ot.fecha_cierre]
    cierres_a_tiempo = sum([1 for ot in ordenes_cerradas if ot.cierre_a_tiempo == True])
    cierres_tardios = sum([1 for ot in ordenes_cerradas if ot.cierre_a_tiempo == False])

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
                # Guardar archivos en el disco
                carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
                os.makedirs(carpeta_ot, exist_ok=True)
                
                for archivo in archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                
                messages.success(request, "✅ Orden creada y archivos guardados correctamente.")
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

    # Obtener archivos del disco
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}/")
    if os.path.exists(carpeta_ot):
        archivos_disponibles = os.listdir(carpeta_ot)
    else:
        archivos_disponibles = []

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, request.FILES, instance=orden)
        if form.is_valid():
            orden.save()

            # Subir nuevos archivos
            nuevos_archivos = request.FILES.getlist("archivos")
            if nuevos_archivos:
                os.makedirs(carpeta_ot, exist_ok=True)
                
                for archivo in nuevos_archivos:
                    ruta_archivo = os.path.join(carpeta_ot, archivo.name)
                    with open(ruta_archivo, "wb+") as destino:
                        for chunk in archivo.chunks():
                            destino.write(chunk)
                
                messages.success(request, "✅ Nuevos archivos subidos correctamente.")

            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)

    return render(request, "administrativa/ordenes/form.html", {
        "form": form,
        "orden": orden,
        "archivos_disponibles": archivos_disponibles,  # ✅ Esto es lo que usa el template
        "title": "Editar Orden de Trabajo",
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
            messages.success(request, "🗑️ Archivo eliminado correctamente.")
        else:
            messages.error(request, "⚠️ Archivo no encontrado.")

    return redirect("administrativa:ordenes:editar_orden", pk=orden.id)


# =====================================================
# ❌ ELIMINAR ORDEN Y CARPETA
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    # Borrar carpeta del disco
    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{orden.numero}")
    
    if os.path.exists(carpeta_ot):
        try:
            # Función para manejar archivos de solo lectura
            def handle_remove_readonly(func, path, exc):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(carpeta_ot, onerror=handle_remove_readonly)
            messages.success(request, "🗑️ Carpeta eliminada correctamente.")
        except Exception as e:
            messages.warning(request, f"⚠️ Error al eliminar carpeta: {e}")

    # Borrar registros en DB
    orden.documentos.all().delete()
    orden.delete()
    messages.success(request, "🗑️ Orden eliminada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 🚫 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    from django.utils import timezone
    
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "cerrada"
    orden.fecha_cierre = timezone.now()
    
    # Calcular si el cierre fue a tiempo
    if orden.fecha_envio:
        fecha_cierre_solo_fecha = orden.fecha_cierre.date()
        fecha_envio_solo_fecha = orden.fecha_envio
        
        if fecha_cierre_solo_fecha <= fecha_envio_solo_fecha:
            orden.cierre_a_tiempo = True
            messages.success(request, "✅ Orden cerrada A TIEMPO correctamente. 😀")
        else:
            orden.cierre_a_tiempo = False
            messages.warning(request, "⚠️ Orden cerrada TARDÍAMENTE. 😞")
    else:
        orden.cierre_a_tiempo = None
        messages.success(request, "✅ Orden cerrada (sin fecha de envío para comparar).")
    
    orden.save()
    return redirect("administrativa:ordenes:listar_ordenes")


# =====================================================
# 📂 DESCARGAR ARCHIVO
# =====================================================
def descargar_archivo(request, numero_ot, nombre_archivo):
    """Descargar archivo del disco de Render"""
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/{nombre_archivo}")
    
    if os.path.exists(ruta_archivo):
        return FileResponse(
            open(ruta_archivo, 'rb'), 
            as_attachment=True, 
            filename=nombre_archivo
        )
    else:
        raise Http404("Archivo no encontrado")