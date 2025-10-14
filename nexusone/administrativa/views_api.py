from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

ngrok_url_actual = None  # variable global temporal

@csrf_exempt
def actualizar_ngrok(request):
    global ngrok_url_actual
    if request.method == "POST":
        data = json.loads(request.body)
        ngrok_url_actual = data.get("url")
        print(f"🌐 Nueva URL ngrok registrada: {ngrok_url_actual}")
        return JsonResponse({"status": "ok", "ngrok_url": ngrok_url_actual})
    return JsonResponse({"error": "Método no permitido"}, status=405)
