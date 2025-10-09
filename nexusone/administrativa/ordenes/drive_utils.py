# ==========================================
# nexusone/utils/drive_utils.py
# ==========================================
import os
import io
import json
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings

# =====================================================
# ⚙️ CONFIGURACIÓN
# =====================================================
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Evita que Google API cree archivos de caché innecesarios
class NoCache(Cache):
    def get(self, url): 
        return None
    def set(self, url, content): 
        pass

# =====================================================
# 🧠 CACHE GLOBAL DE CREDENCIALES Y SERVICIO
# =====================================================
_cached_credentials = None
_service_instance = None


def _get_credentials():
    """
    Devuelve las credenciales del Service Account.
    Reutiliza la instancia en memoria para reducir consumo.
    """
    global _cached_credentials
    if _cached_credentials is not None:
        return _cached_credentials

    json_data = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", None)
    if not json_data:
        raise RuntimeError("No se encontró configuración del Service Account para Google Drive.")

    tmp_path = "/tmp/service_account_drive.json"

    # Crear archivo temporal solo si no existe
    if not os.path.exists(tmp_path):
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(json_data)

    _cached_credentials = service_account.Credentials.from_service_account_file(
        tmp_path, scopes=SCOPES
    )
    return _cached_credentials


def _build_service():
    """
    Construye el cliente de la API de Drive (singleton por worker).
    """
    global _service_instance
    if _service_instance is not None:
        return _service_instance

    creds = _get_credentials()
    _service_instance = build("drive", "v3", credentials=creds, cache=NoCache())
    return _service_instance


# =====================================================
# 🗂️ CREAR CARPETA
# =====================================================
def create_folder(name, parent_id=None):
    """
    Crea una carpeta en Drive dentro de la raíz definida.
    Retorna el ID de la carpeta creada.
    """
    parent_id = parent_id or getattr(settings, "DRIVE_ROOT_FOLDER_ID", None)
    if not parent_id:
        raise ValueError("No se definió DRIVE_ROOT_FOLDER_ID en settings.")

    service = _build_service()
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }

    try:
        folder = service.files().create(body=metadata, fields="id").execute()
        return folder.get("id")
    except Exception as e:
        raise RuntimeError(f"❌ Error creando carpeta en Drive: {e}")


# =====================================================
# ⬆️ SUBIR ARCHIVO
# =====================================================
def upload_file(file_obj, filename, mimetype=None, parent_id=None):
    """
    Sube un archivo al Drive del Service Account.
    Devuelve un dict con {id, webViewLink, webContentLink}.
    Optimizado para no duplicar archivo en memoria.
    """
    parent_id = parent_id or getattr(settings, "DRIVE_ROOT_FOLDER_ID", None)
    if not parent_id:
        raise ValueError("No se definió DRIVE_ROOT_FOLDER_ID en settings.")

    service = _build_service()

    # Detectar tipo MIME
    mimetype = mimetype or getattr(file_obj, "content_type", None) or "application/octet-stream"
    if mimetype == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            mimetype = guessed

    metadata = {"name": filename, "parents": [parent_id]}
    media = MediaIoBaseUpload(file_obj, mimetype=mimetype, resumable=True)

    try:
        created = service.files().create(
            body=metadata, media_body=media, fields="id, webViewLink, webContentLink"
        ).execute()
        file_id = created.get("id")

        # 🔓 Hacer el archivo accesible públicamente
        try:
            service.permissions().create(
                fileId=file_id, body={"type": "anyone", "role": "reader"}
            ).execute()
        except Exception as perm_err:
            print(f"⚠️ No se pudieron asignar permisos públicos: {perm_err}")

        return {
            "id": file_id,
            "webViewLink": created.get("webViewLink"),
            "webContentLink": created.get("webContentLink"),
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"⚠️ Error al subir archivo a Google Drive: {e}")


# =====================================================
# ❌ ELIMINAR ARCHIVO O CARPETA
# =====================================================
def delete_file(file_id):
    """
    Elimina un archivo o carpeta del Drive por su ID.
    Retorna True si fue exitoso, False si falló.
    """
    service = _build_service()
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        print(f"⚠️ Error eliminando archivo: {e}")
        return False
