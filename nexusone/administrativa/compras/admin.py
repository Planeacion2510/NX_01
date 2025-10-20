from django.contrib import admin
from .models import Proveedor, OrdenCompra, DetalleOrden


# -------------------------
# ADMIN PROVEEDOR
# -------------------------
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "telefono", "email", "activo")
    search_fields = ("nombre", "nit", "telefono", "email", "contacto")
    list_filter = ("activo",)
    ordering = ("nombre",)


# -------------------------
# INLINE PARA DETALLES
# -------------------------
class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 1
    fields = ("producto", "cantidad", "precio_unitario", "total")
    readonly_fields = ("total",)

    # ✅ para que Django sepa mostrar la propiedad total
    def total(self, obj):
        return obj.total
    total.short_description = "Total"


# -------------------------
# ADMIN ORDEN DE COMPRA
# -------------------------
@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ("numero", "proveedor", "estado", "fecha_emision", "total")
    search_fields = ("numero", "proveedor__nombre")
    list_filter = ("estado", "fecha_emision")
    ordering = ("-fecha_emision",)
    inlines = [DetalleOrdenInline]
    date_hierarchy = "fecha_emision"
    readonly_fields = ("subtotal", "impuestos", "total")

    # -------------------------
    # ACCIONES PERSONALIZADAS
    # -------------------------
    actions = ["marcar_aprobadas", "marcar_rechazadas", "marcar_cerradas"]

    def marcar_aprobadas(self, request, queryset):
        updated = queryset.update(estado="aprobada")
        self.message_user(request, f"{updated} orden(es) de compra marcadas como Aprobadas ✅")
    marcar_aprobadas.short_description = "Marcar como Aprobadas"

    def marcar_rechazadas(self, request, queryset):
        updated = queryset.update(estado="rechazada")
        self.message_user(request, f"{updated} orden(es) de compra marcadas como Rechazadas ❌")
    marcar_rechazadas.short_description = "Marcar como Rechazadas"

    def marcar_cerradas(self, request, queryset):
        updated = queryset.update(estado="cerrada")
        self.message_user(request, f"{updated} orden(es) de compra marcadas como Cerradas 🔒")
    marcar_cerradas.short_description = "Marcar como Cerradas"
