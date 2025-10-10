# nexusone/administrativa/utils/azure_auth.py
import os
import requests

# ============================================================
# 🔐 Obtener token de Azure con Client Credentials (MS Graph)
# ============================================================
def get_azure_access_token():
    """
    Devuelve un access_token válido para Microsoft Graph,
    usando el flujo 'client_credentials' sin login manual.
    Requiere las variables:
        AZURE_CLIENT_ID
        AZURE_CLIENT_SECRET
        AZURE_TENANT_ID
    """

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise RuntimeError("Faltan variables de entorno Azure: CLIENT_ID / CLIENT_SECRET / TENANT_ID")

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise RuntimeError(f"Error al obtener token: {response.text}")

    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("No se obtuvo access_token en la respuesta de Azure.")

    return token
