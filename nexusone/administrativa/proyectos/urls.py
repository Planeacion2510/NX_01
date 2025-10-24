from django.urls import path
from . import views

app_name = "proyectos"

urlpatterns = [
    # Vista principal
    path("", views.listar_proyectos, name="listar_proyectos"),
    
    # CONSTRUCTORAS
    path("constructora/crear/", views.crear_constructora, name="crear_constructora"),
    path("constructora/<int:pk>/editar/", views.editar_constructora, name="editar_constructora"),
    path("constructora/<int:pk>/eliminar/", views.eliminar_constructora, name="eliminar_constructora"),
    path("constructora/<int:pk>/detalle/", views.detalle_constructora, name="detalle_constructora"),
    
    # PROYECTOS
    path("proyecto/crear/", views.crear_proyecto, name="crear_proyecto"),
    path("proyecto/<int:pk>/editar/", views.editar_proyecto, name="editar_proyecto"),
    path("proyecto/<int:pk>/eliminar/", views.eliminar_proyecto, name="eliminar_proyecto"),
    
    # CONTRATOS
    path("proyecto/<int:pk>/contrato/descargar/", views.descargar_contrato, name="descargar_contrato"),
    path("proyecto/<int:pk>/contrato/eliminar/", views.eliminar_contrato, name="eliminar_contrato"),
]