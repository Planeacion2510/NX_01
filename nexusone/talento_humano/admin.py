from django.contrib import admin
from .models import Empleado, Contrato, Vacacion, Permiso

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("id", "documento", "cargo", "area", "estado")
    search_fields = ("documento", "cargo", "area")
    list_filter = ("estado",)

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("id", "empleado", "tipo", "fecha_inicio", "activo")
    search_fields = ("empleado__user__username", "tipo")
    list_filter = ("activo",)

@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = ("id", "empleado", "fecha_inicio", "fecha_fin", "aprobada")

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ("id", "empleado", "fecha", "motivo", "aprobado")
