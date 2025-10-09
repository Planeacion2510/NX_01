# ==========================================
# nexusone/administrativa/ordenes/views.py
# ==========================================
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator

from .models import OrdenTrabajo, DocumentoOrden
from .forms import OrdenTrabajoForm, DocumentoOrdenForm

# 🔹 Utilidades Google Drive
from .drive_utils import upload_file, delete_file

# =====================================================
# ⚙️ Configuración del FormSet
# =====================================================
DocumentoFormSet = inlineformset_factory(
    OrdenTrabajo, DocumentoOrden, form=DocumentoOrdenForm, extra=1, can_delete=True
)

# =====================================================
# 🔹 LISTAR ORDENES
# =====================================================
def listar_ordenes(request):
    ordenes_qs = (
        OrdenTrabajo.objects.all()
        .order_by("-id")
        .prefetch_related("documentos")
    )

    paginator = Paginator(ordenes_qs, 20)
    page_number = request.GET.get("page")
    ordenes_page = paginator.get_page(page_number)

    for orden in ordenes_page:
        for doc in orden.documentos.all():
            if getattr(doc, "drive_file_id", None):
                doc.drive_view_url = f"https://drive.google.com/file/d/{doc.drive_file_id}/view?usp=sharing"
                doc.drive_download_url = f"https://drive.google.com/uc?id={doc.drive_file_id}&export=download"
            else:
                doc.drive_view_url = ""
                doc.drive_download_url = ""

    return render(
        request,
        "administrativa/ordenes/listar_orden.html",
        {"ordenes": ordenes_page},
    )

# =====================================================
# 🔹 CREAR ORDEN
# =====================================================
def crear_orden(request):
    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST)
        formset = DocumentoFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            orden = form.save()

            for f in formset:
                data = f.cleaned_data
                if not data:
                    continue

                archivo = data.get("archivo")
                nombre = data.get("nombre") or (archivo.name if archivo else "Documento")

                doc = DocumentoOrden.objects.create(orden=orden, nombre=nombre)

                if archivo:
                    try:
                        meta = upload_file(archivo, archivo.name, archivo.content_type)
                        if meta:
                            doc.drive_file_id = meta["id"]
                            doc.drive_view_url = meta.get("webViewLink")
                            doc.drive_download_url = meta.get("webContentLink")
                            doc.save()
                    except Exception as e:
                        print("⚠️ Error subiendo archivo a Drive:", e)

            messages.success(request, "✅ Orden creada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores del formulario.")
    else:
        form = OrdenTrabajoForm()
        formset = DocumentoFormSet()

    return render(
        request,
        "administrativa/ordenes/form.html",
        {"form": form, "formset": formset, "title": "Crear Orden", "orden": None},
    )

# =====================================================
# 🔹 EDITAR ORDEN
# =====================================================
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    if request.method == "POST":
        form = OrdenTrabajoForm(request.POST, instance=orden)
        formset = DocumentoFormSet(request.POST, request.FILES, instance=orden)

        if form.is_valid() and formset.is_valid():
            orden = form.save()

            # Eliminar documentos marcados
            for f in formset.deleted_forms:
                doc = f.instance
                if doc and getattr(doc, "drive_file_id", None):
                    delete_file(doc.drive_file_id)
                doc.delete()

            # Guardar nuevos documentos
            for f in formset.save(commit=False):
                f.orden = orden
                archivo = getattr(f, "archivo", None)
                if archivo:
                    try:
                        meta = upload_file(archivo, archivo.name, archivo.content_type)
                        if meta:
                            f.drive_file_id = meta["id"]
                            f.drive_view_url = meta.get("webViewLink")
                            f.drive_download_url = meta.get("webContentLink")
                    except Exception as e:
                        print("⚠️ Error subiendo archivo a Drive:", e)
                f.save()

            formset.save_m2m()
            messages.success(request, "✅ Orden actualizada correctamente.")
            return redirect("administrativa:ordenes:listar_ordenes")
        else:
            messages.error(request, "⚠️ Corrige los errores antes de continuar.")
    else:
        form = OrdenTrabajoForm(instance=orden)
        formset = DocumentoFormSet(instance=orden)

    return render(
        request,
        "administrativa/ordenes/form.html",
        {"form": form, "formset": formset, "title": f"Editar {orden.numero}", "orden": orden},
    )

# =====================================================
# 🔹 ELIMINAR ORDEN
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)

    for doc in orden.documentos.all():
        if getattr(doc, "drive_file_id", None):
            delete_file(doc.drive_file_id)

    orden.delete()
    messages.success(request, "🗑️ Orden eliminada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")

# =====================================================
# 🔹 CERRAR ORDEN
# =====================================================
def cerrar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    orden.estado = "cerrada"
    orden.save()
    messages.success(request, "✅ Orden cerrada correctamente.")
    return redirect("administrativa:ordenes:listar_ordenes")
