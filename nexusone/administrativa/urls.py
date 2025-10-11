from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "administrativa"

urlpatterns = [
    path("", views.menu_administrativa, name="menu_administrativa"),

    # Módulo Órdenes
    path(
        "ordenes/",
        include(("nexusone.administrativa.ordenes.urls", "ordenes"), namespace="ordenes")
    ),
]

# 🧩 Servir archivos media en entorno local
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
