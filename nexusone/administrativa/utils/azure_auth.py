# nexusone/administrativa/utils/azure_auth.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_azure_access_token():
    """
    Obtiene un token usando client_credentials (app-only).
    Requiere AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_SCOPE, AZURE_TOKEN_URL en env.
    """
    url = os.getenv("AZURE_TOKEN_URL")
    if not url:
        raise RuntimeError("AZURE_TOKEN_URL no definida en el entorno.")
    data = {
        "client_id": os.getenv("AZURE_CLIENT_ID"),
        "scope": os.getenv("AZURE_SCOPE"),
        "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    payload = r.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"No se obtuvo access_token: {payload}")
    return token
