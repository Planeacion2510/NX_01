from django.db import models
from django.utils import timezone


# ==================================================
# CONSTRUCTORA
# ==================================================
class Constructora(models.Model):
    nombre = models.CharField("Nombre", max_length=200)
    nit = models.CharField("NIT", max_length=50, unique=True)
    direccion = models.CharField("Dirección", max_length=250, blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=50, blank=True, null=True)
    email = models.EmailField("Correo electrónico", blank=True, null=True)
    contacto = models.CharField("Persona de contacto", max_length=150, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Constructora"
        verbose_name_plural = "Constructoras"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==================================================
# PROYECTO
# ==================================================
class Proyecto(models.Model):
    ESTADOS = [
        ("planeado", "Planeado"),
        ("ejecucion", "En Ejecución"),
        ("finalizado", "Finalizado"),
        ("suspendido", "Suspendido"),
    ]
    ESTADOS_FINANCIEROS = [
        ("estable", "Estable"),
        ("critico", "Crítico"),
        ("sin_definir", "Sin definir"),
    ]

    constructora = models.ForeignKey(
        Constructora,
        on_delete=models.CASCADE,
        related_name="proyectos"
    )
    codigo = models.CharField("Código", max_length=50, unique=True)
    nombre = models.CharField("Nombre del Proyecto", max_length=200)
    descripcion = models.TextField("Descripción", blank=True, null=True)
    ubicacion = models.CharField("Ubicación", max_length=250, blank=True, null=True)
    estado = models.CharField("Estado", max_length=20, choices=ESTADOS, default="planeado")
    estado_financiero = models.CharField("Estado Financiero", max_length=20, choices=ESTADOS_FINANCIEROS, default="sin_definir")
    porcentaje_avance = models.DecimalField("Avance (%)", max_digits=5, decimal_places=2, default=0)
    valor_total = models.DecimalField("Valor Total", max_digits=15, decimal_places=2, default=0)
    valor_pagado = models.DecimalField("Valor Pagado", max_digits=15, decimal_places=2, default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ==================================================
# PRESUPUESTO DE COMPRAS
# ==================================================
class PresupuestoCompras(models.Model):
    """
    Control de presupuestos asignados a un proyecto específico.
    Se usa para vincular las órdenes de compra (OrdenCompra)
    y controlar cuánto se ha comprometido o ejecutado.
    """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='presupuestos_compras',
        verbose_name='Proyecto'
    )

    nombre = models.CharField(
        max_length=150,
        verbose_name='Nombre del Presupuesto',
        help_text='Ejemplo: Presupuesto Fase 1 - Estructura'
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción o alcance del presupuesto'
    )

    monto_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Monto Total Asignado'
    )

    monto_comprometido = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Monto Comprometido (OC aprobadas)'
    )

    monto_ejecutado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Monto Ejecutado (OC recibidas / cerradas)'
    )

    creado = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )

    actualizado = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Presupuesto Activo'
    )

    class Meta:
        verbose_name = 'Presupuesto de Compras'
        verbose_name_plural = 'Presupuestos de Compras'
        ordering = ['-creado']

    def __str__(self):
        return f"{self.nombre} - {self.proyecto.nombre}"

    @property
    def monto_libre(self):
        """Saldo disponible"""
        return self.monto_total - (self.monto_comprometido + self.monto_ejecutado)

    @property
    def porcentaje_ejecutado(self):
        if self.monto_total > 0:
            return round((self.monto_ejecutado / self.monto_total) * 100, 2)
        return 0

    @property
    def porcentaje_comprometido(self):
        if self.monto_total > 0:
            return round((self.monto_comprometido / self.monto_total) * 100, 2)
        return 0


# ==================================================
# ITEM CONTRATADO
# ==================================================
class ItemContratado(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="items_contratados"
    )
    item = models.CharField("Descripción del ítem", max_length=200)
    unidad = models.CharField("Unidad", max_length=50, blank=True, null=True)
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2, default=0)
    valor_unitario = models.DecimalField("Valor Unitario", max_digits=15, decimal_places=2, default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item Contratado"
        verbose_name_plural = "Items Contratados"
        ordering = ["proyecto", "item"]

    @property
    def valor_total(self):
        return self.cantidad * self.valor_unitario

    def __str__(self):
        return f"{self.item} ({self.proyecto.nombre})"


# ==================================================
# APU (Análisis de Precios Unitarios)
# ==================================================
class APU(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=150, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=True)
    costo_materiales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    costo_mano_obra = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    costo_equipos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    otros_costos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to="apu_imagenes/", null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "APU"
        verbose_name_plural = "APUs"
        ordering = ["nombre"]

    @property
    def costo_total(self):
        return (
            self.costo_materiales +
            self.costo_mano_obra +
            self.costo_equipos +
            self.otros_costos
        )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
