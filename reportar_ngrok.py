import requests
import time
import json
import subprocess

def obtener_url_ngrok():
    """Obtiene la URL pública de ngrok desde la API local"""
    try:
        res = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = res.json()
        for tunnel in data.get("tunnels", []):
            if tunnel.get("public_url", "").startswith("https://"):
                return tunnel["public_url"]
    except Exception as e:
        print("⚠️ No se pudo obtener URL de ngrok:", e)
    return None


def enviar_a_render(url):
    """Envía la URL de ngrok a Render usando curl (para evitar bug WinError 10022)"""
    endpoint = "https://nx-01.onrender.com/administrativa/api/actualizar-ngrok/"
    payload = json.dumps({"url": url})

    comando = [
        "curl",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", payload,
        endpoint
    ]

    print("📡 Enviando URL a Render con curl...")
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=15
        )
        if resultado.returncode == 0:
            print(f"✅ URL enviada correctamente a Render: {url}")
        else:
            print(f"❌ Error al enviar: {resultado.stderr}")
    except Exception as e:
        print("⚠️ Error al ejecutar curl:", e)


if __name__ == "__main__":
    print("⏳ Esperando a que ngrok esté listo...")
    for i in range(20, 0, -1):
        print(f"⏳ Iniciando en {i}s...", end="\r")
        time.sleep(1)
    print()

    url = obtener_url_ngrok()
    if url:
        print(f"🔗 URL detectada: {url}")
        enviar_a_render(url)
    else:
        print("⚠️ No se encontró URL pública de ngrok.")
