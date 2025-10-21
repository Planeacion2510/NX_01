from django.db import models
from django.utils import timezone
from datetime import date
from nexusone.administrativa.compras.models import Proveedor  # 🔗 importamos

# ---------------------------
# INSUMOS
# ---------------------------
class Insumo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    
    # 🆕 PROVEEDOR (reemplaza descripción)
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='insumos',
        verbose_name='Proveedor'
    )
    
    unidad = models.CharField(max_length=20, help_text="Ej: kg, litros, unidades")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Stock
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(default=0)

    # IVA y Descuento
    iva = models.DecimalField("IVA (%)", max_digits=5, decimal_places=2, default=19)
    descuento_proveedor = models.DecimalField("Descuento Proveedor (%)", max_digits=5, decimal_places=2, default=0)

    @property
    def stock_actual(self):
        entradas = self.movimientos.filter(tipo="entrada").aggregate(models.Sum("cantidad"))["cantidad__sum"] or 0
        salidas = self.movimientos.filter(tipo="salida").aggregate(models.Sum("cantidad"))["cantidad__sum"] or 0
        return entradas - salidas

    @property
    def precio_con_iva(self):
        return self.precio_unitario * (1 + self.iva / 100)

    @property
    def precio_total(self):
        precio_iva = self.precio_unitario * (1 + self.iva / 100)
        precio_desc = precio_iva * (1 - self.descuento_proveedor / 100)
        return precio_desc * self.stock_actual

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (Stock: {self.stock_actual})"


# ---------------------------
# MOVIMIENTOS DE KARDEX
# ---------------------------
class MovimientoKardex(models.Model):
    TIPO_CHOICES = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.tipo} {self.cantidad} {self.insumo.nombre} ({self.fecha.date()})"


# ---------------------------
# HERRAMIENTAS
# ---------------------------
class Herramienta(models.Model):
    nombre = models.CharField("Nombre", max_length=100)
    descripcion = models.TextField("Descripción", blank=True)
    cantidad = models.PositiveIntegerField("Cantidad", default=0)
    responsable = models.CharField("Responsable", max_length=100, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class MovimientoHerramienta(models.Model):
    TIPO_CHOICES = [
        ("asignacion", "Asignación"),
        ("devolucion", "Devolución"),
        ("baja", "Baja"),
    ]
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField("Tipo de Movimiento", max_length=20, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField("Cantidad")
    descripcion = models.TextField("Descripción", blank=True)
    fecha = models.DateField("Fecha", default=timezone.now)

    def __str__(self):
        return f"{self.tipo.upper()} - {self.herramienta.nombre} ({self.cantidad})"


# ---------------------------
# MAQUINARIA
# ---------------------------
class Maquinaria(models.Model):
    serial = models.CharField("Serial", max_length=50, unique=True)
    nombre = models.CharField("Nombre", max_length=100)
    marca = models.CharField("Marca", max_length=100)
    fecha_compra = models.DateField("Fecha de Compra", null=True, blank=True)
    cantidad = models.PositiveIntegerField("Cantidad", default=1)
    responsable = models.CharField("Responsable", max_length=100, blank=True)

    manual = models.FileField(
        "Manual",
        upload_to='manuales/',
        null=True,
        blank=True,
        help_text="Archivo PDF del manual de la maquinaria"
    )

    creado = models.DateTimeField(auto_now_add=True)

    # 🆕 MÉTODO PARA CALCULAR TIEMPO DE USO
    @property
    def tiempo_uso(self):
        """
        Calcula el tiempo de uso desde la fecha de compra hasta hoy
        Retorna un string en formato: "X años Y días" o "X días"
        """
        if not self.fecha_compra:
            return "Sin fecha de compra"
        
        hoy = date.today()
        diferencia = hoy - self.fecha_compra
        dias_totales = diferencia.days
        
        # Si es menos de un año, solo mostrar días
        if dias_totales < 365:
            return f"{dias_totales} días"
        
        # Calcular años y días restantes
        años = dias_totales // 365
        dias_restantes = dias_totales % 365
        
        # Formato de salida
        if dias_restantes == 0:
            return f"{años} año{'s' if años != 1 else ''}"
        else:
            return f"{años} año{'s' if años != 1 else ''} {dias_restantes} día{'s' if dias_restantes != 1 else ''}"
    
    # 🔄 MÉTODO ANTERIOR (para compatibilidad)
    @property
    def anios_uso(self):
        """Método antiguo que retorna solo los años (para compatibilidad)"""
        if not self.fecha_compra:
            return 0
        diferencia = date.today() - self.fecha_compra
        return diferencia.days // 365

    def __str__(self):
        return f"{self.nombre} ({self.marca})"


class MovimientoMaquinaria(models.Model):
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, related_name="movimientos")
    cantidad = models.PositiveIntegerField("Cantidad")
    descripcion = models.TextField("Descripción", blank=True)
    fecha = models.DateField("Fecha", default=timezone.now)

    def __str__(self):
        return f"{self.maquinaria.nombre} - {self.cantidad}"