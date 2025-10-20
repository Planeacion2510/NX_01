from django.urls import path, include
from . import views

app_name = "administrativa"

urlpatterns = [
    # Menú principal de Dirección Administrativa
    path("", views.menu_administrativa, name="menu_administrativa"),
    
    # Submódulos
    path("ordenes/", include("nexusone.administrativa.ordenes.urls")),
    path("inventario/", include("nexusone.administrativa.inventario.urls")),
    path("compras/", include("nexusone.administrativa.compras.urls")),
]