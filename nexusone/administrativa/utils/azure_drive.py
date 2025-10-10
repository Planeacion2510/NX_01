# nexusone/administrativa/utils/azure_drive.py
import os
import requests
from nexusone.administrativa.utils.azure_auth import get_azure_access_token

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
ROOT_FOLDER = os.getenv("ONEDRIVE_ROOT_FOLDER", "DinnovaERP")

# -------------------------
# Helpers: drive + folders
# -------------------------
def _get_first_drive_id(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{GRAPH_BASE_URL}/drives", headers=headers)
    r.raise_for_status()
    drives = r.json().get("value", [])
    if not drives:
        raise RuntimeError("No se encontraron drives disponibles en el tenant.")
    return drives[0]["id"]

def _ensure_folder_hierarchy(token, drive_id, folder_path):
    """
    Asegura que exista la ruta de carpetas en OneDrive, creando cada segmento si hace falta.
    folder_path: "DinnovaERP/Ordenes/00001"
    Devuelve el item-id del último segmento (parent folder id).
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    parts = [p for p in folder_path.split("/") if p.strip()]
    parent_id = None  # empezamos en root
    for i, part in enumerate(parts):
        # Construir path relativo hasta este segmento
        path = "/".join(parts[: i + 1])
        # Intentar obtener item por path
        url_get = f"{GRAPH_BASE_URL}/drives/{drive_id}/root:/{path}"
        r = requests.get(url_get, headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            item = r.json()
            parent_id = item["id"]
            continue
        elif r.status_code == 404:
            # Crear carpeta en el padre
            if parent_id:
                parent_children_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{parent_id}/children"
            else:
                parent_children_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root/children"

            body = {"name": part, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}
            r2 = requests.post(parent_children_url, headers=headers, json=body)
            r2.raise_for_status()
            item = r2.json()
            parent_id = item["id"]
        else:
            # otro error
            r.raise_for_status()
    return parent_id

# -------------------------
# Operaciones principales
# -------------------------
def list_files_in_folder(module_name="Ordenes", order_number=None):
    """
    Lista archivos en la carpeta /ROOT_FOLDER/{module_name}/[order_number]
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)
    # construir ruta
    path = f"{ROOT_FOLDER}/{module_name}"
    if order_number:
        path = f"{path}/{order_number}"
    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root:/{path}:/children"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json().get("value", [])

def upload_file(local_file_path, filename, module_name="Ordenes", order_number=None):
    """
    Sube el archivo a /ROOT_FOLDER/{module_name}/{order_number}/filename
    Devuelve el JSON con id, webUrl, etc.
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)

    # aseguramos carpeta
    folder_path = f"{ROOT_FOLDER}/{module_name}"
    if order_number:
        folder_path = f"{folder_path}/{order_number}"
    # obtain target parent id
    parent_id = _ensure_folder_hierarchy(token, drive_id, folder_path)

    # cargar archivo apuntando al parent item id:
    # endpoint: /drives/{driveId}/items/{parentId}:/{filename}:/content
    upload_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{parent_id}:/{filename}:/content"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}

    with open(local_file_path, "rb") as fh:
        r = requests.put(upload_url, headers=headers, data=fh)
    r.raise_for_status()
    return r.json()

def delete_file(item_id):
    """
    Elimina un archivo por item id en el drive.
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)
    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(url, headers=headers)
    if r.status_code in (204, 200):
        return True
    else:
        r.raise_for_status()

def get_file_download_link(item_id):
    """
    Obtiene webUrl o link para descarga (según lo devuelva Graph).
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)
    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()
