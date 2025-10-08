import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive"]

# =====================================================
# 🔐 CREDENCIALES
# =====================================================

def _get_credentials():
    """
    Obtiene las credenciales del Service Account desde settings.
    Compatible con Render (usa JSON en variable de entorno si aplica).
    """
    if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None):
        return service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

    if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", None):
        tmp_path = os.path.join("/tmp", "service_account_drive.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        return service_account.Credentials.from_service_account_file(tmp_path, scopes=SCOPES)

    raise RuntimeError(
        "No Google service account configuration found. "
        "Set GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON in settings."
    )

# =====================================================
# ⚙️ CONSTRUCCIÓN DEL SERVICIO
# =====================================================

def _build_service():
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds, cache_discovery=False)

# =====================================================
# 🗂️ CREAR CARPETA
# =====================================================

def create_folder(name, parent_id=None):
    """
    Crea una carpeta en Google Drive dentro de 'parent_id' (si se indica).
    Devuelve el ID de la carpeta creada.
    """
    service = _build_service()
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]

    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")

# =====================================================
# ⬆️ SUBIR ARCHIVO
# =====================================================

def upload_file(file_obj, filename, mimetype=None, parent_id=None):
    """
    Sube un archivo al Drive del service account.
    file_obj: Django UploadedFile (.file)
    filename: nombre con que se guardará
    mimetype: tipo MIME (si no se indica se intenta deducir)
    parent_id: carpeta destino
    """
    service = _build_service()

    # Aseguramos que el archivo se lea desde memoria
    if hasattr(file_obj, "read"):
        file_stream = io.BytesIO(file_obj.read())
    else:
        raise ValueError("El objeto de archivo no es válido o no tiene método read().")

    # Validar tipo MIME
    mimetype = mimetype or getattr(file_obj, "content_type", "application/octet-stream")
    if not mimetype or mimetype == "application/octet-stream":
        # Fallback: intentar inferirlo por extensión
        import mimetypes
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            mimetype = guessed

    # Crear metadata y cuerpo
    body = {"name": filename}
    if parent_id:
        body["parents"] = [parent_id]

    media = MediaIoBaseUpload(file_stream, mimetype=mimetype, resumable=True)

    try:
        created = service.files().create(
            body=body, media_body=media, fields="id, webViewLink, webContentLink"
        ).execute()
        file_id = created.get("id")

        # Permitir acceso por enlace (si lo soporta)
        perm = {"type": "anyone", "role": "reader"}
        try:
            service.permissions().create(fileId=file_id, body=perm).execute()
        except Exception:
            pass  # Ignora si el dominio bloquea permisos públicos

        # Obtener URLs finales
        meta = service.files().get(fileId=file_id, fields="webViewLink, webContentLink").execute()

        return {
            "id": file_id,
            "webViewLink": meta.get("webViewLink"),
            "webContentLink": meta.get("webContentLink"),
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Error al subir archivo a Google Drive: {str(e)}")

# =====================================================
# ❌ ELIMINAR ARCHIVO
# =====================================================

def delete_file(file_id):
    """
    Elimina un archivo del Drive por su ID.
    Devuelve True si fue exitoso.
    """
    service = _build_service()
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception:
        return False
