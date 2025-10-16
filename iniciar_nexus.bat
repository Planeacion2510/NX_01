import requests
import json
import time

# ===== Esperar unos segundos por si ngrok aún no está listo =====
time.sleep(2)

try:
    # Leer info de ngrok
    r = requests.get("http://127.0.0.1:4040/api/tunnels")
    data = r.json()
    tunnel_url = data['tunnels'][0]['public_url']
    
    print(f"🔗 URL detectada: {tunnel_url}")

    # Enviar URL a Render (endpoint que hayas definido para actualizar NGROK_URL)
    render_endpoint = "https://nx-01.onrender.com/administrativa/ordenes/actualizar-ngrok/"
    response = requests.post(render_endpoint, json={"ngrok_url": tunnel_url}, timeout=10)

    if response.status_code == 200:
        print(f"✅ URL enviada correctamente a Render: {tunnel_url}")
    else:
        print(f"⚠️ Error enviando URL a Render: {response.text}")

except Exception as e:
    print(f"❌ Error detectando ngrok o enviando URL: {e}")
