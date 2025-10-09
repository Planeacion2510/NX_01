import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import OrdenTrabajo
from .forms import OrdenTrabajoForm
from .drive_utils import upload_file, delete_file

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
    DocumentoFormSet = modelformset_factory(Documento, form=DocumentoForm, extra=1, can_delete=True)
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST)
        formset = DocumentoFormSet(request.POST, request.FILES, queryset=Documento.objects.none())

        if form.is_valid() and formset.is_valid():
            orden = form.save()
            for f in formset.cleaned_data:
                if f and f.get("archivo"):
                    archivo = f["archivo"]
                    nombre = f["nombre"] or archivo.name
                    result = upload_file(archivo, nombre)
                    Documento.objects.create(
                        orden=orden,
                        nombre=nombre,
                        archivo_drive_id=result["id"],
                        enlace=result["webViewLink"],
                    )
            messages.success(request, "✅ Orden y documentos guardados correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm()
        formset = DocumentoFormSet(queryset=Documento.objects.none())

    return render(request, "ordenes/crear_orden.html", {
        "form": form,
        "formset": formset,
        "title": "Crear Orden de Trabajo",
    })

# =====================================================
# ✏️ EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    DocumentoFormSet = modelformset_factory(Documento, form=DocumentoForm, extra=1, can_delete=True)

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        formset = DocumentoFormSet(request.POST, request.FILES, queryset=orden.documentos.all())

        if form.is_valid() and formset.is_valid():
            form.save()
            for f in formset.cleaned_data:
                if f.get("DELETE") and f.get("id"):
                    delete_file(f["id"].archivo_drive_id)
                    f["id"].delete()
                elif f.get("archivo"):
                    archivo = f["archivo"]
                    nombre = f["nombre"] or archivo.name
                    result = upload_file(archivo, nombre)
                    Documento.objects.create(
                        orden=orden,
                        nombre=nombre,
                        archivo_drive_id=result["id"],
                        enlace=result["webViewLink"],
                    )
            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm(instance=orden)
        formset = DocumentoFormSet(queryset=orden.documentos.all())

    return render(request, "ordenes/crear_orden.html", {
        "form": form,
        "formset": formset,
        "title": "Editar Orden de Trabajo",
        "orden": orden,
    })

# =====================================================
# ❌ ELIMINAR ORDEN
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    for doc in orden.documentos.all():
        delete_file(doc.archivo_drive_id)
        doc.delete()
    orden.delete()
    messages.success(request, "🗑️ Orden y documentos eliminados.")
    return redirect("administrativa:ordenes:listar_ordenes")

# =====================================================
# 🚫 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "Cerrada"
    orden.save()
    messages.success(request, "✅ Orden cerrada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")
