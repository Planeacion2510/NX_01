import requests
import time
import json
import socket

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

def enviar_a_render(url, intentos=5, espera=5):
    """Envía la URL de ngrok a Render con reintentos automáticos"""
    endpoint = "https://nx-01.onrender.com/administrativa/api/actualizar-ngrok/"
    headers = {"Content-Type": "application/json"}

    for intento in range(1, intentos + 1):
        try:
            # 🔧 Forzar IPv4 para evitar fallos DNS con urllib3
            original_getaddrinfo = socket.getaddrinfo
            socket.getaddrinfo = lambda *args, **kwargs: original_getaddrinfo(args[0], args[1], socket.AF_INET, *args[2:], **kwargs)

            res = requests.post(endpoint, json={"url": url}, headers=headers, timeout=10)
            if res.status_code == 200:
                print(f"✅ URL enviada correctamente a Render: {url}")
                return True
            else:
                print(f"❌ Error al enviar (intento {intento}/{intentos}): {res.status_code} - {res.text}")
        except Exception as e:
            print(f"⚠️ Error de conexión (intento {intento}/{intentos}):", e)

        # Restaurar función original
        socket.getaddrinfo = original_getaddrinfo
        time.sleep(espera)

    print("❌ No se pudo conectar con Render después de varios intentos.")
    return False


if __name__ == "__main__":
    print("⏳ Esperando a que ngrok esté listo...")
    time.sleep(10)
    url = obtener_url_ngrok()
    if url:
        enviar_a_render(url)
    else:
        print("⚠️ No se encontró URL pública de ngrok.")

