from django.contrib import admin
from .models import (
    Insumo,
    MovimientoKardex,
    Herramienta,
    MovimientoHerramienta,
    Maquinaria,
    MovimientoMaquinaria,
)

# ---- Insumos ----
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "stock_minimo", "stock_maximo", "stock_actual_display")
    search_fields = ("nombre",)

    def stock_actual_display(self, obj):
        return obj.stock_actual()
    stock_actual_display.short_description = "Stock actual"

# ---- Kardex ----
@admin.register(MovimientoKardex)
class MovimientoKardexAdmin(admin.ModelAdmin):
    list_display = ("insumo", "tipo", "cantidad", "fecha", "observacion")
    list_filter = ("tipo", "fecha")
    search_fields = ("insumo__nombre",)
    ordering = ("-fecha",)


# ---- Herramientas ----
@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad", "responsable", "creado")
    search_fields = ("nombre", "responsable")
    ordering = ("nombre",)


@admin.register(MovimientoHerramienta)
class MovimientoHerramientaAdmin(admin.ModelAdmin):
    list_display = ("herramienta", "tipo", "cantidad", "fecha")
    list_filter = ("tipo", "fecha")
    search_fields = ("herramienta__nombre",)
    ordering = ("-fecha",)


# ---- Maquinaria ----
@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ("serial", "nombre", "marca", "responsable", "fecha_compra", "cantidad")
    search_fields = ("serial", "nombre", "marca", "responsable")
    list_filter = ("marca", "responsable")
    ordering = ("nombre",)


@admin.register(MovimientoMaquinaria)
class MovimientoMaquinariaAdmin(admin.ModelAdmin):
    list_display = ("maquinaria", "cantidad", "descripcion", "fecha")
    list_filter = ("fecha",)
    search_fields = ("maquinaria__nombre", "descripcion")
    ordering = ("-fecha",)
