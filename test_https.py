import requests
import socket

socket.setdefaulttimeout(10)
try:
    print("🌍 Probando conexión a Render...")
    res = requests.get("https://nx-01.onrender.com", timeout=10)
    print(f"✅ Conexión exitosa: {res.status_code}")
except Exception as e:
    print("❌ Error al conectar con Render:", e)
