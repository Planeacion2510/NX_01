import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def recibir_archivos_local(request):
    """
    Este endpoint corre en tu PC (a través del túnel ngrok).
    Guarda los archivos subidos físicamente en OneDrive.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero_ot = request.POST.get("numero_ot")
    archivos = request.FILES.getlist("archivos")

    if not numero_ot:
        return JsonResponse({"error": "Falta número de OT"}, status=400)

    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/")
    os.makedirs(carpeta_ot, exist_ok=True)

    guardados = []
    for archivo in archivos:
        ruta_archivo = os.path.join(carpeta_ot, archivo.name)
        with open(ruta_archivo, "wb+") as destino:
            for chunk in archivo.chunks():
                destino.write(chunk)
        guardados.append(archivo.name)

    return JsonResponse({"status": "ok", "archivos": guardados})
