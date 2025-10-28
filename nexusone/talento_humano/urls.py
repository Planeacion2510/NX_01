from django.urls import path
from . import views

app_name = "talento_humano"

urlpatterns = [
    path("", views.menu_talento_humano, name="menu_talento_humano"),

    # Empleados
    path("empleados/", views.lista_empleados, name="lista_empleados"),
    path("empleados/nuevo/", views.nuevo_empleado, name="nuevo_empleado"),

    # Contratos
    path("contratos/", views.lista_contratos, name="lista_contratos"),
    path("contratos/nuevo/", views.nuevo_contrato, name="nuevo_contrato"),

    # Vacaciones
    path("vacaciones/", views.lista_vacaciones, name="lista_vacaciones"),
    path("vacaciones/nuevo/", views.nueva_vacacion, name="nueva_vacacion"),

    # Permisos → ahora en gestion_empleado
    path("gestion_empleado/permisos/", views.lista_permisos, name="lista_permisos"),
    path("gestion_empleado/permisos/nuevo/", views.nuevo_permiso, name="nuevo_permiso"),

    # Reglamentos
    path("gestion_empleado/reglamentos/", views.lista_reglamentos, name="lista_reglamentos"),
    path("gestion_empleado/reglamentos/nuevo/", views.nuevo_reglamento, name="nuevo_reglamento"),

    # Memorandos
    path("gestion_empleado/memorandos/", views.lista_memorandos, name="lista_memorandos"),
    path("gestion_empleado/memorandos/nuevo/", views.nuevo_memorando, name="nuevo_memorando"),
]
