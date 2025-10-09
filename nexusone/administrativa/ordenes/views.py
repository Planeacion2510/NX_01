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

# ===========================
# 🔹 GOOGLE DRIVE (UTILS CENTRALIZADO)
# ===========================
from nexusone.utils.drive_utils import (
    create_folder,
    upload_file,
    delete_file,
)

# =====================================================
# ⚙️ OPTIMIZACIÓN: crear el FormSet una sola vez (no por request)
# =====================================================
DocumentoFormSet = inlineformset_factory(
    OrdenTrabajo, DocumentoOrden, form=DocumentoOrdenForm, extra=1, can_delete=True
)

# =====================================================
# 🔹 LISTAR ORDENES (con paginación y optimización)
# =====================================================
def listar_ordenes(request):
    """
    Lista las órdenes de trabajo con paginación y URLs de Drive pre-generadas.
    """
    # Prefetch evita consultas repetidas y reduce RAM
    ordenes_qs = (
        OrdenTrabajo.objects.all()
        .order_by("-id")
        .prefetch_related("documentos")
    )

    # Paginación: 20 órdenes por página
    paginator = Paginator(ordenes_qs, 20)
    page_number = request.GET.get("page")
    ordenes_page = paginator.get_page(page_number)

    # Generar URLs públicas solo para las órdenes en la página actual
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

            # Crear carpeta OT en Drive
            folder_id = None
            try:
                folder_name = f"OT_{orden.numero}"
                folder_id = create_folder(folder_name)
            except Exception as e:
                print("❌ Error creando carpeta en Drive:", e)

            # Subir documentos a Drive
            for f in formset:
                data = f.cleaned_data
                if not data:
                    continue

                archivo = data.get("archivo")
                nombre = data.get("nombre") or (archivo.name if archivo else "Documento")

                doc = DocumentoOrden.objects.create(orden=orden, nombre=nombre)

                if archivo and folder_id:
                    try:
                        meta = upload_file(archivo, archivo.name, archivo.content_type, parent_id=folder_id)
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
        {"form": form, "formset": formset, "title": "Crear Orden"},
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

            # Crear o reutilizar carpeta OT
            folder_id = None
            try:
                folder_name = f"OT_{orden.numero}"
                folder_id = create_folder(folder_name)
            except Exception as e:
                print("❌ Error creando carpeta en Drive:", e)

            # Eliminar documentos marcados
            for f in formset.deleted_forms:
                doc = f.instance
                if doc and getattr(doc, "drive_file_id", None):
                    delete_file(doc.drive_file_id)
                doc.delete()

            # Subir nuevos documentos
            for f in formset.save(commit=False):
                f.orden = orden
                archivo = getattr(f, "archivo", None)

                if archivo and folder_id:
                    try:
                        meta = upload_file(archivo, archivo.name, archivo.content_type, parent_id=folder_id)
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
        {"form": form, "formset": formset, "title": f"Editar {orden.numero}"},
    )


# =====================================================
# 🔹 ELIMINAR ORDEN
# =====================================================
def eliminar_orden(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    try:
        # Buscar y eliminar la carpeta OT en Drive
        from nexusone.utils.drive_utils import _build_service

        service = _build_service()
        query = (
            f"mimeType='application/vnd.google-apps.folder' "
            f"and name='OT_{orden.numero}' "
            f"and '{settings.DRIVE_ROOT_FOLDER_ID}' in parents "
            f"and trashed=false"
        )
        folders = service.files().list(q=query, fields="files(id)").execute().get("files", [])
        if folders:
            folder_id = folders[0]["id"]

            # Eliminar archivos dentro
            children = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false", fields="files(id)"
            ).execute().get("files", [])
            for c in children:
                service.files().delete(fileId=c["id"]).execute()

            # Eliminar carpeta principal
            service.files().delete(fileId=folder_id).execute()
    except Exception as e:
        print("⚠️ Error eliminando carpeta en Drive:", e)

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
