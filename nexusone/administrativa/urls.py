from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import views_api  # ✅ se agrega correctamente el import

app_name = "administrativa"

urlpatterns = [
    path("", views.menu_administrativa, name="menu_administrativa"),

    # Módulo Órdenes
    path(
        "ordenes/",
        include(("nexusone.administrativa.ordenes.urls", "ordenes"), namespace="ordenes")
    ),

    # Endpoint para recibir la URL de ngrok desde tu PC
    path("api/actualizar-ngrok/", views_api.actualizar_ngrok, name="actualizar_ngrok"),
]

# ✅ Soporte para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
