from django.urls import path
from . import views

app_name = "ordenes"

urlpatterns = [
    path("", views.listar_ordenes, name="listar_ordenes"),
    path("crear/", views.crear_orden, name="crear_orden"),
    path("editar/<int:pk>/", views.editar_orden, name="editar_orden"),
    path("eliminar/<int:pk>/", views.eliminar_orden, name="eliminar_orden"),
    path("cerrar/<int:pk>/", views.cerrar_orden, name="cerrar_orden"),
    path("documento/eliminar/<int:pk>/", views.eliminar_documento, name="eliminar_documento"),
    path("recibir-archivos-local/", views_upload.recibir_archivos_local, name="recibir_archivos_local"),
]
