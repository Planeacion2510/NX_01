import requests
import time
import json

def obtener_url_ngrok():
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
    try:
        endpoint = "https://nx-01.onrender.com/api/actualizar-ngrok/"
        res = requests.post(endpoint, json={"url": url})
        if res.status_code == 200:
            print(f"✅ URL enviada correctamente a Render: {url}")
        else:
            print(f"❌ Error al enviar: {res.text}")
    except Exception as e:
        print("❌ Error al conectar con Render:", e)

if __name__ == "__main__":
    print("⏳ Esperando a que ngrok esté listo...")
    time.sleep(10)
    url = obtener_url_ngrok()
    if url:
        enviar_a_render(url)
    else:
        print("⚠️ No se encontró URL pública de ngrok.")

