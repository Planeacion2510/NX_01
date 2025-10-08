from django.urls import path, include
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
