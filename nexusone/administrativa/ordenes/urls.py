from django.urls import path
from . import views, views_upload  # views_upload maneja ngrok

app_name = "ordenes"

urlpatterns = [
    # =======================
    # Funciones principales
    # =======================
    path("", views.listar_ordenes, name="listar_ordenes"),
    path("crear/", views.crear_orden, name="crear_orden"),
    path("editar/<int:pk>/", views.editar_orden, name="editar_orden"),
    path("eliminar/<int:pk>/", views.eliminar_orden, name="eliminar_orden"),
    path("cerrar/<int:pk>/", views.cerrar_orden, name="cerrar_orden"),
    path("documento/eliminar/<int:pk>/", views.eliminar_documento, name="eliminar_documento"),

    # =======================
    # Endpoints ngrok (local PC)
    # =======================
    path("recibir-archivos-local/", views_upload.recibir_archivos_local, name="recibir_archivos_local"),
    path("eliminar-orden-local/", views_upload.eliminar_orden_local, name="eliminar_orden_local"),
    path("descargar-archivo/<str:numero_ot>/<str:filename>/", views_upload.descargar_archivo, name="descargar_archivo"),

    # =======================
    # Endpoint seguro para Render
    # =======================
    path("descargar-archivo-render/<str:numero_ot>/<str:nombre_archivo>/", 
         views.descargar_archivo_render, name="descargar_archivo_render"),
]
