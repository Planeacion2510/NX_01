from django.urls import path
from . import views

app_name = "ordenes"

urlpatterns = [
    # 🧾 CRUD de órdenes de trabajo
    path("", views.listar_ordenes, name="listar_ordenes"),
    path("crear/", views.crear_orden, name="crear_orden"),
    path("editar/<int:pk>/", views.editar_orden, name="editar_orden"),
    path("cerrar/<int:pk>/", views.cerrar_orden, name="cerrar_orden"),
    path("eliminar/<int:pk>/", views.eliminar_orden, name="eliminar_orden"),
]
