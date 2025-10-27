# nexusone/administrativa/compras/models.py
from django.db import models
from django.utils import timezone


# ==================================================
# PROVEEDOR (sin cambios)
# ==================================================
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


# ==================================================
# ORDEN DE COMPRA (MODIFICADA - con nuevos campos)
# ==================================================
class OrdenCompra(models.Model):
    ESTADOS = [
        ("generada", "Generada"),          # 🆕 Nueva (automática sin revisar)
        ("borrador", "Borrador"),
        ("pendiente", "Pendiente Aprobación"),
        ("aprobada", "Aprobada"),
        ("ejecutada", "Ejecutada"),        # 🆕 Compra realizada
        ("recibida", "Recibida"),          # 🆕 Material recibido
        ("rechazada", "Rechazada"),
        ("cerrada", "Cerrada"),
    ]

    DESTINOS = [
        ("constructora", "Constructora"),
        ("proyecto", "Proyecto"),
        ("interna", "Compra Interna"),
    ]
    
    ORIGEN_CHOICES = [
        ("manual", "Manual"),
        ("automatica", "Automática"),
    ]
    
    # ═══════════════════════════════════════════════
    # CAMPOS BÁSICOS (existentes)
    # ═══════════════════════════════════════════════
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="ordenes",
        null=True,
        blank=True
    )
    orden_trabajo = models.ForeignKey(
        "ordenes.OrdenTrabajo",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ordenes_compra"
    )
    numero = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="N° Orden",
        editable=False
    )
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
    
    # ═══════════════════════════════════════════════
    # 🆕 NUEVOS CAMPOS
    # ═══════════════════════════════════════════════
    
    # Origen de la OC
    origen = models.CharField(
        "Origen",
        max_length=15,
        choices=ORIGEN_CHOICES,
        default="manual",
        help_text="Manual: creada por usuario. Automática: generada por el sistema"
    )
    
    # Vinculación a proyectos
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_compra',
        verbose_name='Proyecto'
    )
    
    # Control de presupuesto
    presupuesto_compras = models.ForeignKey(
        'proyectos.PresupuestoCompras',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_compra',
        verbose_name='Presupuesto de Compras'
    )
    presupuesto_disponible_al_crear = models.DecimalField(
        "Presupuesto Disponible al Crear",
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Snapshot del presupuesto disponible al momento de crear la OC"
    )
    presupuesto_suficiente = models.BooleanField(
        "Presupuesto Suficiente",
        default=True
    )

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ["-fecha_emision"]

    def save(self, *args, **kwargs):
        """Generar número automático y validar presupuesto"""
        # Generar número si no tiene
        if not self.numero:
            ultimo = OrdenCompra.objects.all().order_by("id").last()
            if not ultimo:
                nuevo_numero = 1
            else:
                nuevo_numero = int(ultimo.numero) + 1
            self.numero = str(nuevo_numero).zfill(5)
        
        # Validar presupuesto al crear (solo para OCs con presupuesto asignado)
        if not self.pk and self.presupuesto_compras:
            presupuesto_libre = self.presupuesto_compras.monto_libre
            self.presupuesto_disponible_al_crear = presupuesto_libre
            self.presupuesto_suficiente = self.total <= presupuesto_libre
        
        super().save(*args, **kwargs)
        
        # Actualizar presupuesto si está vinculado
        if self.presupuesto_compras:
            self._actualizar_presupuesto()
    
    def _actualizar_presupuesto(self):
        """Actualiza los montos del presupuesto según el estado de la OC"""
        presupuesto = self.presupuesto_compras
        
        # Calcular totales de todas las OCs de este presupuesto
        ocs_aprobadas = OrdenCompra.objects.filter(
            presupuesto_compras=presupuesto,
            estado__in=['aprobada', 'generada', 'pendiente']
        ).aggregate(models.Sum('total'))['total__sum'] or 0
        
        ocs_ejecutadas = OrdenCompra.objects.filter(
            presupuesto_compras=presupuesto,
            estado__in=['ejecutada', 'recibida', 'cerrada']
        ).aggregate(models.Sum('total'))['total__sum'] or 0
        
        # Actualizar presupuesto
        presupuesto.monto_comprometido = ocs_aprobadas
        presupuesto.monto_ejecutado = ocs_ejecutadas
        presupuesto.save(update_fields=['monto_comprometido', 'monto_ejecutado'])

    def __str__(self):
        if self.proyecto:
            return f"Orden {self.numero} - {self.proyecto.nombre}"
        elif self.proveedor:
            return f"Orden {self.numero} - {self.proveedor}"
        else:
            return f"Orden {self.numero}"


# ==================================================
# DETALLE ORDEN (sin cambios)
# ==================================================
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
        """Calcula el total de este producto"""
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto} x {self.cantidad} (Orden {self.orden.numero})"