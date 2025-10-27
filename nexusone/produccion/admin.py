# nexusone/produccion/admin.py
from django.contrib import admin
from .models import (
    AvanceProduccion,
    AsignacionOperario,
    MaterialOrden,
    PausaProduccion
)


# ==================================================
# AVANCE PRODUCCIÓN
# ==================================================
@admin.register(AvanceProduccion)
class AvanceProduccionAdmin(admin.ModelAdmin):
    list_display = (
        'orden',
        'cantidad_avance',
        'cantidad_acumulada',
        'registrado_por',
        'fecha_registro'
    )
    list_filter = ('fecha_registro', 'registrado_por')
    search_fields = ('orden__numero', 'observaciones')
    readonly_fields = ('cantidad_acumulada', 'fecha_registro')
    date_hierarchy = 'fecha_registro'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('orden', 'registrado_por')


# ==================================================
# ASIGNACIÓN OPERARIO
# ==================================================
@admin.register(AsignacionOperario)
class AsignacionOperarioAdmin(admin.ModelAdmin):
    list_display = (
        'orden',
        'operario',
        'fecha_asignacion',
        'fecha_finalizacion',
        'activo'
    )
    list_filter = ('activo', 'fecha_asignacion')
    search_fields = ('orden__numero', 'operario__username', 'operario__first_name')
    date_hierarchy = 'fecha_asignacion'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('orden', 'operario')


# ==================================================
# MATERIAL ORDEN
# ==================================================
@admin.register(MaterialOrden)
class MaterialOrdenAdmin(admin.ModelAdmin):
    list_display = (
        'orden',
        'insumo',
        'cantidad_requerida',
        'cantidad_asignada',
        'cantidad_utilizada',
        'estado'
    )
    list_filter = ('estado', 'fecha_asignacion')
    search_fields = ('orden__numero', 'insumo__nombre', 'insumo__codigo')
    readonly_fields = ('fecha_asignacion',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('orden', 'insumo', 'asignado_por')


# ==================================================
# PAUSA PRODUCCIÓN
# ==================================================
@admin.register(PausaProduccion)
class PausaProduccionAdmin(admin.ModelAdmin):
    list_display = (
        'orden',
        'motivo',
        'fecha_inicio',
        'fecha_fin',
        'activa',
        'registrado_por'
    )
    list_filter = ('motivo', 'activa', 'fecha_inicio')
    search_fields = ('orden__numero', 'descripcion')
    readonly_fields = ('fecha_inicio',)
    date_hierarchy = 'fecha_inicio'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('orden', 'registrado_por')