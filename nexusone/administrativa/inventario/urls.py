from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.index_inventario, name="index_inventario"),

    # ---- Insumos ----
    path("insumos/", views.lista_insumo, name="lista_insumo"),
    path("insumos/nuevo/", views.nuevo_insumo, name="nuevo_insumo"),
    path("insumos/editar/<int:pk>/", views.editar_insumo, name="editar_insumo"),
    path("insumos/eliminar/<int:pk>/", views.eliminar_insumo, name="eliminar_insumo"),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),

    # ---- Maquinaria ----
    path("maquinaria/", views.lista_maquinaria, name="lista_maquinaria"),
    path("maquinaria/nueva/", views.nueva_maquinaria, name="nueva_maquinaria"),
    path("maquinaria/<int:pk>/editar/", views.editar_maquinaria, name="editar_maquinaria"),
    path("maquinaria/<int:pk>/eliminar/", views.eliminar_maquinaria, name="eliminar_maquinaria"),

    # ---- Herramientas ----
    path("herramientas/", views.lista_herramientas, name="lista_herramientas"),
    path("herramientas/nueva/", views.nueva_herramienta, name="nueva_herramienta"),
    path("herramientas/<int:pk>/editar/", views.editar_herramienta, name="editar_herramienta"),
    path("herramientas/<int:pk>/eliminar/", views.eliminar_herramienta, name="eliminar_herramienta"),

    # ---- Kardex ----
    path("kardex/", views.listar_kardex, name="listar_kardex"),
    path("kardex/nuevo/", views.registrar_movimiento_kardex, name="nuevo_movimiento"),
    path("kardex/editar/<int:pk>/", views.editar_movimiento, name="editar_movimiento"),
    path("kardex/eliminar/<int:pk>/", views.eliminar_movimiento, name="eliminar_movimiento"),
]
