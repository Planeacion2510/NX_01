# nexusone/talento_humano/urls.py
from django.urls import path
from . import views

app_name = "talento_humano"

urlpatterns = [
    path("", views.menu_talento_humano, name="menu_talento_humano"),
    path("empleados/", views.lista_empleados, name="lista_empleados"),
    path("empleados/<int:pk>/", views.detalle_empleado, name="detalle_empleado"),
    path("contratos/nuevo/", views.nuevo_contrato, name="nuevo_contrato"),
    path("vacaciones/", views.lista_vacaciones, name="lista_vacaciones"),
    path("permisos/", views.lista_permisos, name="lista_permisos"),
]
