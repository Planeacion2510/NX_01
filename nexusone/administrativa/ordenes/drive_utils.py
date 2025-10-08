from googleapiclient.discovery import build
from googleapiclient.discovery_cache.base import Cache
from google.oauth2 import service_account
import io, os, json
from googleapiclient.http import MediaIoBaseUpload
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Evitar caché pesado del cliente de Google
class NoCache(Cache):
    def get(self, url): return None
    def set(self, url, content): pass

def _get_credentials():
    if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None):
        return service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

    if getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", None):
        tmp_path = os.path.join("/tmp", "service_account_drive.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        return service_account.Credentials.from_service_account_file(tmp_path, scopes=SCOPES)

    raise RuntimeError("No Google service account configuration found.")

def _build_service():
    creds = _get_credentials()
    # 👇 Aquí usamos el cache minimalista
    return build("drive", "v3", credentials=creds, cache=NoCache())


# =====================================================
# 🗂️ CREAR CARPETA
# =====================================================
def create_folder(name, parent_id=ROOT_DRIVE_FOLDER):
    """
    Crea una carpeta en Google Drive dentro de la carpeta raíz (por defecto).
    Devuelve el ID de la carpeta creada.
    """
    service = _build_service()
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder.get("id")

# =====================================================
# ⬆️ SUBIR ARCHIVO
# =====================================================
def upload_file(file_obj, filename, mimetype=None, parent_id=ROOT_DRIVE_FOLDER):
    """
    Sube un archivo al Drive del service account.
    Devuelve un diccionario con {id, webViewLink, webContentLink}.
    """
    service = _build_service()

    # Asegurar que se pueda leer el archivo
    if not hasattr(file_obj, "read"):
        raise ValueError("El objeto de archivo no tiene método read().")

    file_stream = io.BytesIO(file_obj.read())

    # Detectar tipo MIME
    mimetype = mimetype or getattr(file_obj, "content_type", None) or "application/octet-stream"
    if mimetype == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(filename)
        if guessed:
            mimetype = guessed

    metadata = {"name": filename, "parents": [parent_id]}
    media = MediaIoBaseUpload(file_stream, mimetype=mimetype, resumable=True)

    try:
        created = service.files().create(
            body=metadata, media_body=media, fields="id, webViewLink, webContentLink"
        ).execute()
        file_id = created.get("id")

        # 🔓 Permitir acceso por enlace (público)
        try:
            service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"},
            ).execute()
        except Exception as perm_err:
            print(f"⚠️ No se pudieron asignar permisos públicos: {perm_err}")

        # Retornar datos del archivo
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
    Devuelve True si fue exitoso, False si falló.
    """
    service = _build_service()
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        print(f"⚠️ Error eliminando archivo: {e}")
        return False
