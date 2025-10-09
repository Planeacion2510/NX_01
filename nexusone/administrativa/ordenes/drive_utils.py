from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings
import io, os, mimetypes

# =====================================================
# ⚙️ CONFIGURACIÓN
# =====================================================
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Evita caché grande en disco
class NoCache(Cache):
    def get(self, url): return None
    def set(self, url, content): pass

# =====================================================
# 🧠 CACHE GLOBAL
# =====================================================
_cached_credentials = None
_service_instance = None

def _get_credentials():
    """Devuelve las credenciales del Service Account (reusadas)."""
    global _cached_credentials
    if _cached_credentials is not None:
        return _cached_credentials

    if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", None):
        tmp_path = "/tmp/service_account.json"
        if not os.path.exists(tmp_path):
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        _cached_credentials = service_account.Credentials.from_service_account_file(
            tmp_path, scopes=SCOPES
        )
        return _cached_credentials
    raise RuntimeError("❌ No se encontró configuración del Service Account.")

def _build_service():
    """Construye el cliente de Drive (único por proceso)."""
    global _service_instance
    if _service_instance:
        return _service_instance
    creds = _get_credentials()
    _service_instance = build("drive", "v3", credentials=creds, cache=NoCache())
    return _service_instance

# =====================================================
# ⬆️ SUBIR ARCHIVO DIRECTO
# =====================================================
def upload_file(file_obj, filename, mimetype=None):
    """
    Sube un archivo directamente a la carpeta compartida de Drive.
    Devuelve: {id, webViewLink, webContentLink}
    """
    parent_id = getattr(settings, "DRIVE_ROOT_FOLDER_ID", None)
    if not parent_id:
        raise ValueError("❌ Falta DRIVE_ROOT_FOLDER_ID en settings.")

    service = _build_service()
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
        file_id = created["id"]

        # 🔓 Permitir acceso público
        service.permissions().create(
            fileId=file_id, body={"type": "anyone", "role": "reader"}
        ).execute()

        return {
            "id": file_id,
            "webViewLink": created.get("webViewLink"),
            "webContentLink": created.get("webContentLink"),
        }

    except Exception as e:
        raise RuntimeError(f"⚠️ Error al subir a Drive: {e}")

# =====================================================
# ❌ ELIMINAR ARCHIVO
# =====================================================
def delete_file(file_id):
    """Elimina un archivo del Drive."""
    service = _build_service()
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        print(f"⚠️ Error eliminando archivo: {e}")
        return False
