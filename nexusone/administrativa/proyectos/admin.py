from django.contrib import admin
from .models import Constructora, Proyecto, ItemContratado


# ===================================
# 🏢 ADMIN CONSTRUCTORA
# ===================================
@admin.register(Constructora)
class ConstructoraAdmin(admin.ModelAdmin):
    list_display = [
        'razon_social', 
        'nit', 
        'telefono', 
        'correo', 
        'total_proyectos',
        'proyectos_activos',
        'activa', 
        'creado'
    ]
    list_filter = ['activa', 'creado']
    search_fields = ['razon_social', 'nit', 'correo', 'representante_legal']
    readonly_fields = ['creado', 'actualizado']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'nit')
        }),
        ('Contacto', {
            'fields': ('telefono', 'correo', 'ubicacion', 'representante_legal', 'contacto_adicional')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'activa')
        }),
        ('Control', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    def total_proyectos(self, obj):
        """Muestra el total de proyectos en el admin"""
        return obj.total_proyectos
    total_proyectos.short_description = 'Total Proyectos'
    
    def proyectos_activos(self, obj):
        """Muestra los proyectos activos en el admin"""
        return obj.proyectos_activos
    proyectos_activos.short_description = 'Proyectos Activos'


# ===================================
# 📋 ADMIN ITEM CONTRATADO (INLINE)
# ===================================
class ItemContratadoInline(admin.TabularInline):
    model = ItemContratado
    extra = 1
    fields = ['item', 'medida', 'cantidad', 'valor_unitario', 'valor_total_display']
    readonly_fields = ['valor_total_display']
    
    def valor_total_display(self, obj):
        """Muestra el valor total del ítem"""
        if obj.id:
            return f"${obj.valor_total:,.2f}"
        return "—"
    valor_total_display.short_description = 'Valor Total'


# ===================================
# 🏗️ ADMIN PROYECTO
# ===================================
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo',
        'nombre',
        'constructora',
        'tipo_proyecto',
        'estado',
        'fecha_inicio',
        'fecha_fin_estimada',
        'presupuesto',
        'activo',
        'creado'
    ]
    list_filter = ['estado', 'tipo_proyecto', 'activo', 'creado', 'constructora']
    search_fields = ['codigo', 'nombre', 'constructora__razon_social', 'ubicacion_proyecto']
    readonly_fields = ['creado', 'actualizado', 'duracion_dias', 'dias_transcurridos', 'porcentaje_tiempo']
    date_hierarchy = 'fecha_inicio'
    inlines = [ItemContratadoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('constructora', 'codigo', 'nombre', 'tipo_proyecto', 'numero_unidades')
        }),
        ('Ubicación', {
            'fields': ('ubicacion_proyecto',)
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_estimada', 'fecha_fin_real', 'estado')
        }),
        ('Información Calculada', {
            'fields': ('duracion_dias', 'dias_transcurridos', 'porcentaje_tiempo'),
            'classes': ('collapse',)
        }),
        ('Financiero', {
            'fields': ('presupuesto',)
        }),
        ('Contrato', {
            'fields': ('contrato',)
        }),
        ('Control', {
            'fields': ('activo', 'creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
    
    def duracion_dias(self, obj):
        """Muestra la duración del proyecto"""
        return obj.duracion_dias if obj.duracion_dias else '—'
    duracion_dias.short_description = 'Duración (días)'
    
    def dias_transcurridos(self, obj):
        """Muestra los días transcurridos"""
        return obj.dias_transcurridos if obj.dias_transcurridos else '—'
    dias_transcurridos.short_description = 'Días Transcurridos'
    
    def porcentaje_tiempo(self, obj):
        """Muestra el porcentaje de tiempo transcurrido"""
        if obj.porcentaje_tiempo:
            return f"{obj.porcentaje_tiempo:.1f}%"
        return '—'
    porcentaje_tiempo.short_description = '% Tiempo'


# ===================================
# 📋 ADMIN ITEM CONTRATADO (STANDALONE)
# ===================================
@admin.register(ItemContratado)
class ItemContratadoAdmin(admin.ModelAdmin):
    list_display = ['item', 'proyecto', 'medida', 'cantidad', 'valor_unitario', 'valor_total_display', 'creado']
    list_filter = ['proyecto__constructora', 'creado']
    search_fields = ['item', 'proyecto__nombre', 'proyecto__codigo']
    readonly_fields = ['creado', 'actualizado', 'valor_total_display']
    
    def valor_total_display(self, obj):
        """Muestra el valor total del ítem"""
        return f"${obj.valor_total:,.2f}"
    valor_total_display.short_description = 'Valor Total'