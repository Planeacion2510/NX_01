# nexusone/talento_humano/admin.py
from django.contrib import admin
from .models import Empleado, Contrato, DocumentoEmpresa, Vacacion, Permiso, LlamadoAtencion

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("user", "cargo", "area", "estado", "fecha_ingreso")
    search_fields = ("user__username", "user__first_name", "user__last_name", "cargo")

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_inicio", "fecha_fin", "salario")

@admin.register(DocumentoEmpresa)
class DocumentoEmpresaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "fecha_publicacion")

@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_inicio", "fecha_fin", "aprobado")

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "motivo", "fecha", "aprobado")

@admin.register(LlamadoAtencion)
class LlamadoAtencionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "motivo", "fecha", "tipo")
