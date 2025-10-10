import os
import requests
from nexusone.administrativa.utils.azure_auth import get_azure_access_token

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
ROOT_FOLDER = os.getenv("ONEDRIVE_FOLDER_PATH", "DinnovaERP")

# ============================================================
# 🔧 Funciones internas
# ============================================================

def _get_first_drive_id(token: str) -> str:
    """
    Obtiene el ID del primer drive disponible (OneDrive de la cuenta conectada)
    """
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{GRAPH_BASE_URL}/me/drives", headers=headers)
    r.raise_for_status()
    drives = r.json().get("value", [])
    if not drives:
        raise RuntimeError("❌ No se encontraron drives disponibles en la cuenta de OneDrive.")
    return drives[0]["id"]

def _ensure_folder_hierarchy(token: str, drive_id: str, folder_path: str) -> str:
    """
    Verifica o crea la jerarquía de carpetas en OneDrive.
    Devuelve el ID de la última carpeta del path.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    parts = [p for p in folder_path.split("/") if p.strip()]
    parent_id = None  # Comienza desde root

    for i, part in enumerate(parts):
        path = "/".join(parts[: i + 1])
        url_get = f"{GRAPH_BASE_URL}/drives/{drive_id}/root:/{path}"
        r = requests.get(url_get, headers=headers)

        if r.status_code == 200:
            item = r.json()
            parent_id = item["id"]
            continue
        elif r.status_code == 404:
            # Crear carpeta
            if parent_id:
                create_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{parent_id}/children"
            else:
                create_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root/children"

            body = {
                "name": part,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename",
            }
            r2 = requests.post(create_url, headers=headers, json=body)
            r2.raise_for_status()
            item = r2.json()
            parent_id = item["id"]
        else:
            r.raise_for_status()

    return parent_id

# ============================================================
# 🚀 Funciones principales
# ============================================================

def upload_file(local_file_path, filename, module_name="Ordenes", order_number=None, make_public=True):
    """
    📤 Sube un archivo a OneDrive en la carpeta:
        /ROOT_FOLDER/{module_name}/{order_number}/{filename}
    Retorna información del archivo (id, nombre, url, etc).
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)

    # Crear ruta de destino
    folder_path = f"{ROOT_FOLDER}/{module_name}"
    if order_number:
        folder_path = f"{folder_path}/{order_number}"

    parent_id = _ensure_folder_hierarchy(token, drive_id, folder_path)

    # Subir el archivo
    upload_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{parent_id}:/{filename}:/content"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}

    with open(local_file_path, "rb") as fh:
        r = requests.put(upload_url, headers=headers, data=fh)
    r.raise_for_status()
    file_info = r.json()

    # Si se desea, crear enlace público de lectura
    if make_public:
        try:
            share_url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{file_info['id']}/createLink"
            share_body = {"type": "view", "scope": "anonymous"}
            share_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            s = requests.post(share_url, headers=share_headers, json=share_body)
            if s.status_code == 200:
                link_info = s.json()
                file_info["publicUrl"] = link_info.get("link", {}).get("webUrl")
        except Exception as e:
            print(f"⚠️ No se pudo crear el enlace público: {e}")

    return file_info


def list_files_in_folder(module_name="Ordenes", order_number=None):
    """
    📋 Lista archivos en la carpeta /ROOT_FOLDER/{module_name}/{order_number}
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)

    path = f"{ROOT_FOLDER}/{module_name}"
    if order_number:
        path = f"{path}/{order_number}"

    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/root:/{path}:/children"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("value", [])


def delete_file(item_id):
    """
    🗑️ Elimina un archivo por su ID
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)

    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(url, headers=headers)
    if r.status_code in (204, 200):
        return True
    r.raise_for_status()


def get_file_download_link(item_id):
    """
    🔗 Devuelve información del archivo (incluye webUrl y downloadUrl)
    """
    token = get_azure_access_token()
    drive_id = _get_first_drive_id(token)

    url = f"{GRAPH_BASE_URL}/drives/{drive_id}/items/{item_id}?expand=thumbnails"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    result = {
        "name": data.get("name"),
        "webUrl": data.get("webUrl"),
        "downloadUrl": data.get("@microsoft.graph.downloadUrl"),
        "size": data.get("size"),
    }
    return result

