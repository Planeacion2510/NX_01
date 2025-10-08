from django.contrib import admin
from .models import OrdenTrabajo


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = ("numero", "constructora", "proyecto", "proceso", "estado", "fecha_apertura", "fecha_cierre")
    list_filter = ("estado", "fecha_apertura", "fecha_cierre")
    search_fields = ("numero", "constructora", "proyecto")
    ordering = ("-fecha_apertura",)
    date_hierarchy = "fecha_apertura"
