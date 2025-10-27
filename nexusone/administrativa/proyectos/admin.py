from django.contrib import admin
from .models import Constructora, Proyecto, ItemContratado, APU


# ===================================
# 🏢 ADMIN CONSTRUCTORA
# ===================================
@admin.register(Constructora)
class ConstructoraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'telefono', 'email', 'contacto', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'nit', 'contacto', 'email')
    readonly_fields = ()
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nit')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion', 'contacto')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


# ===================================
# 📋 ADMIN ITEM CONTRATADO (INLINE)
# ===================================
class ItemContratadoInline(admin.TabularInline):
    model = ItemContratado
    extra = 1
    fields = ['item', 'unidad', 'cantidad', 'valor_unitario', 'valor_total_display']
    readonly_fields = ['valor_total_display']

    def valor_total_display(self, obj):
        if obj.id:
            return f"${obj.valor_total:,.2f}"
        return "—"
    valor_total_display.short_description = 'Valor Total'


# ===================================
# 🏗️ ADMIN PROYECTO
# ===================================
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'constructora',
        'estado',
        'estado_financiero',
        'porcentaje_avance',
        'valor_total',
        'valor_pagado',
        'creado',
    )
    list_filter = ('estado', 'estado_financiero', 'constructora')
    search_fields = ('codigo', 'nombre', 'constructora__nombre')
    readonly_fields = ('creado', 'actualizado')
    inlines = [ItemContratadoInline]


# ===================================
# 📋 ADMIN ITEM CONTRATADO (STANDALONE)
# ===================================
@admin.register(ItemContratado)
class ItemContratadoAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'proyecto',
        'unidad',
        'cantidad',
        'valor_unitario',
        'valor_total_display',
    )
    list_filter = ('proyecto',)
    search_fields = ('item', 'proyecto__nombre', 'proyecto__codigo')
    readonly_fields = ('valor_total_display',)

    def valor_total_display(self, obj):
        return f"${obj.valor_total:,.2f}"
    valor_total_display.short_description = 'Valor Total'


# ===================================
# ⚙️ ADMIN APU
# ===================================
@admin.register(APU)
class APUAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'activo', 'creado', 'actualizado')
    list_filter = ('categoria', 'activo')
    search_fields = ('codigo', 'nombre')
    readonly_fields = ('creado', 'actualizado')
