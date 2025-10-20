from django.urls import path
from . import views

app_name = "compras"

urlpatterns = [
    path("", views.index_compras, name="index_compras"),

    path("proveedores/", views.lista_proveedores, name="lista_proveedores"),
    path("proveedores/nuevo/", views.nuevo_proveedor, name="nuevo_proveedor"),
    path("proveedores/editar/<int:pk>/", views.editar_proveedor, name="editar_proveedor"),
    path("proveedores/eliminar/<int:pk>/", views.eliminar_proveedor, name="eliminar_proveedor"),

    path("ordenes/", views.lista_ordenes, name="lista_ordenes"),
    path("ordenes/nueva/", views.crear_orden, name="crear_orden"),
    path("ordenes/editar/<int:pk>/", views.editar_orden, name="editar_orden"),
    path("ordenes/eliminar/<int:pk>/", views.eliminar_orden, name="eliminar_orden"),
]
