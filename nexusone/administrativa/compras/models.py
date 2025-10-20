from django.db import models
from django.utils import timezone


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre / Razón Social")
    nit = models.CharField(max_length=20, unique=True, verbose_name="NIT / Documento")
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Persona de contacto")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.nit})"


class OrdenCompra(models.Model):
    ESTADOS = [
        ("borrador", "Borrador"),
        ("pendiente", "Pendiente Aprobación"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
        ("cerrada", "Cerrada"),
    ]

    DESTINOS = [
        ("constructora", "Constructora"),
        ("proyecto", "Proyecto"),
        ("interna", "Compra Interna"),
    ]

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="ordenes",
        null=True, blank=True
    )
    orden_trabajo = models.ForeignKey(
        "ordenes.OrdenTrabajo",
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="ordenes_compra"
    )
    numero = models.CharField(max_length=30, unique=True, verbose_name="N° Orden", editable=False)
    fecha_emision = models.DateField(default=timezone.now)
    fecha_entrega = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    destino = models.CharField(
        max_length=20,
        choices=DESTINOS,
        default="proyecto",
        verbose_name="Destino de la orden"
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ["-fecha_emision"]

    def save(self, *args, **kwargs):
        if not self.numero:  # Solo asigna número si no tiene
            ultimo = OrdenCompra.objects.all().order_by("id").last()
            if not ultimo:
                nuevo_numero = 1
            else:
                nuevo_numero = int(ultimo.numero) + 1
            self.numero = str(nuevo_numero).zfill(5)  # Formato 00001, 00002...
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orden {self.numero} - {self.proveedor}"


class DetalleOrden(models.Model):
    orden = models.ForeignKey(
        OrdenCompra,
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    producto = models.CharField(max_length=200, verbose_name="Producto / Servicio")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Detalle de Orden"
        verbose_name_plural = "Detalles de Órdenes"

    @property
    def total(self):
        """Calcula el total de este producto sin guardarlo en la BD"""
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto} x {self.cantidad} (Orden {self.orden.numero})"
