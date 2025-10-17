from django.urls import path, include
from . import views

app_name = "administrativa"

urlpatterns = [
    # 👉 Ruta al menú administrativo principal
    path("menu/", views.menu_administrativa, name="menu_administrativa"),

    # 👉 Subrutas existentes (por ejemplo: órdenes)
    path("ordenes/", include("nexusone.administrativa.ordenes.urls")),
]
