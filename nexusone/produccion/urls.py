# nexusone/produccion/urls.py
from django.urls import path
from . import views

app_name = "produccion"

urlpatterns = [
    # Menú principal
    path("", views.menu_produccion, name="menu_produccion"),
    
    # Dashboard
    path("dashboard/", views.dashboard_produccion, name="dashboard"),
    
    # Órdenes de trabajo (vista operativa)
    path("ordenes/", views.lista_ordenes_produccion, name="lista_ordenes"),
    path("ordenes/<int:pk>/", views.detalle_orden, name="detalle_orden"),
    
    # Control de producción
    path("ordenes/<int:pk>/avance/", views.registrar_avance, name="registrar_avance"),
    path("ordenes/<int:pk>/estado/", views.cambiar_estado_orden, name="cambiar_estado"),
    path("ordenes/<int:pk>/asignar/", views.asignar_operario, name="asignar_operario"),
    path("ordenes/<int:pk>/pausar/", views.pausar_orden, name="pausar_orden"),
    path("ordenes/<int:pk>/reanudar/", views.reanudar_orden, name="reanudar_orden"),
]