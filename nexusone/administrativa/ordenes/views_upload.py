import os
import shutil
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests

# 🔹 Usar la URL de ngrok definida en settings
NGROK_URL = getattr(settings, "NGROK_URL", "").rstrip("/") + "/"

@csrf_exempt
def recibir_archivos_local(request):
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


@csrf_exempt
def eliminar_orden_local(request):
    """Elimina completamente la carpeta de una orden en tu PC"""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero_ot = request.POST.get("numero_ot")
    if not numero_ot:
        return JsonResponse({"error": "Falta número de OT"}, status=400)

    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}")
    
    print(f"🔍 Intentando eliminar: {carpeta_ot}")
    print(f"🔍 ¿Existe? {os.path.exists(carpeta_ot)}")
    
    if os.path.exists(carpeta_ot):
        try:
            # Usar shutil.rmtree con onerror para manejar permisos en Windows
            def handle_remove_readonly(func, path, exc):
                """Maneja archivos de solo lectura en Windows"""
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(carpeta_ot, onerror=handle_remove_readonly)
            print(f"✅ Carpeta eliminada completamente: {carpeta_ot}")
            
            # Verificar que realmente se eliminó
            if not os.path.exists(carpeta_ot):
                return JsonResponse({
                    "status": "ok", 
                    "mensaje": f"✅ Carpeta {numero_ot} eliminada completamente de tu PC"
                })
            else:
                return JsonResponse({
                    "status": "warning",
                    "mensaje": f"⚠️ La carpeta {numero_ot} aún existe después de intentar eliminarla"
                })
                
        except PermissionError as e:
            print(f"❌ Error de permisos: {str(e)}")
            return JsonResponse({
                "status": "error",
                "mensaje": f"❌ Falta de permisos para eliminar: {str(e)}"
            }, status=500)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return JsonResponse({
                "status": "error",
                "mensaje": f"❌ Error al eliminar carpeta: {str(e)}"
            }, status=500)
    else:
        print(f"ℹ️ Carpeta no encontrada: {carpeta_ot}")
        return JsonResponse({
            "status": "ok", 
            "mensaje": f"ℹ️ No existe la carpeta {numero_ot} en tu PC"
        })


@csrf_exempt
def eliminar_archivo_local(request):
    """✅ Endpoint para eliminar un archivo específico"""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero_ot = request.POST.get("numero_ot")
    archivo = request.POST.get("archivo")
    
    if not numero_ot or not archivo:
        return JsonResponse({"error": "Faltan parámetros"}, status=400)

    ruta_archivo = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/{archivo}")
    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)
        return JsonResponse({"status": "ok", "mensaje": f"Archivo {archivo} eliminado"})
    else:
        return JsonResponse({"status": "error", "mensaje": "Archivo no encontrado"}, status=404)


@csrf_exempt
def descargar_archivo(request, numero_ot, filename):
    """
    Descargar un archivo de tu PC vía ngrok
    """
    if not NGROK_URL:
        return HttpResponse("URL de ngrok no configurada.", status=400)

    url_pc = f"{NGROK_URL}Ordenes/{numero_ot}/{filename}"
    try:
        r = requests.get(url_pc)
        if r.status_code == 200:
            response = HttpResponse(r.content, content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return HttpResponse("Archivo no encontrado en la PC.", status=404)
    except Exception as e:
        return HttpResponse(f"Error al conectar con la PC: {e}", status=500)


@csrf_exempt
def listar_archivos_local(request):
    numero_ot = request.GET.get("numero_ot")
    if not numero_ot:
        return JsonResponse({"error": "Falta número de OT"}, status=400)

    carpeta_ot = os.path.join(settings.MEDIA_ROOT, f"Ordenes/{numero_ot}/")
    if os.path.exists(carpeta_ot):
        archivos = os.listdir(carpeta_ot)
        return JsonResponse({"archivos": archivos})
    else:
        return JsonResponse({"archivos": []})