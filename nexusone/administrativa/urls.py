from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import views_api  # ✅ import correcto

app_name = "administrativa"

urlpatterns = [
    path("", views.menu_administrativa, name="menu_administrativa"),

    # Módulo Órdenes
    path(
        "ordenes/",
        include(("nexusone.administrativa.ordenes.urls", "ordenes"), namespace="ordenes")
    ),

    # Endpoint API para recibir la URL ngrok
    path("api/actualizar-ngrok/", views_api.actualizar_ngrok, name="actualizar_ngrok"),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
