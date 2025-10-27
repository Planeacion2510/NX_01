# nexusone/administrativa/proyectos/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal


# ==================================================
# CONSTRUCTORA (MANTENER - ya existe)
# ==================================================
class Constructora(models.Model):
    nombre = models.CharField("Nombre", max_length=200)
    nit = models.CharField("NIT", max_length=20, unique=True)
    direccion = models.CharField("Dirección", max_length=300, blank=True)
    telefono = models.CharField("Teléfono", max_length=50, blank=True)
    email = models.EmailField("Email", blank=True)
    contacto = models.CharField("Persona de Contacto", max_length=100, blank=True)
    activo = models.BooleanField("Activo", default=True)
    
    class Meta:
        verbose_name = "Constructora"
        verbose_name_plural = "Constructoras"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ==================================================
# PROYECTO (EXPANDIR - agregar campos)
# ==================================================
class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('cotizacion', 'En Cotización'),
        ('aprobado', 'Aprobado'),
        ('en_ejecucion', 'En Ejecución'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    ESTADO_FINANCIERO_CHOICES = [
        ('pendiente', 'Pendiente Anticipo'),
        ('anticipo_recibido', 'Anticipo Recibido'),
        ('en_cortes', 'En Cortes'),
        ('liquidado', 'Liquidado'),
    ]
    
    # Campos básicos (ya existen)
    constructora = models.ForeignKey(
        Constructora, 
        on_delete=models.PROTECT,
        related_name='proyectos',
        verbose_name='Constructora'
    )
    codigo = models.CharField("Código", max_length=50, unique=True)
    nombre = models.CharField("Nombre del Proyecto", max_length=200)
    ubicacion = models.CharField("Ubicación", max_length=300, blank=True)
    descripcion = models.TextField("Descripción", blank=True)
    
    # 🆕 NUEVOS CAMPOS
    estado = models.CharField(
        "Estado", 
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='cotizacion'
    )
    estado_financiero = models.CharField(
        "Estado Financiero",
        max_length=30,
        choices=ESTADO_FINANCIERO_CHOICES,
        default='pendiente'
    )
    porcentaje_avance = models.DecimalField(
        "% Avance",
        max_digits=5,
        decimal_places=2,
        default=0
    )
    fecha_inicio = models.DateField("Fecha de Inicio", null=True, blank=True)
    fecha_fin_estimada = models.DateField("Fecha Fin Estimada", null=True, blank=True)
    fecha_fin_real = models.DateField("Fecha Fin Real", null=True, blank=True)
    
    # Montos
    valor_total = models.DecimalField(
        "Valor Total",
        max_digits=15,
        decimal_places=2,
        default=0
    )
    valor_pagado = models.DecimalField(
        "Valor Pagado",
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Auditoría
    observaciones = models.TextField("Observaciones", blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proyectos_creados'
    )
    
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def valor_pendiente(self):
        """Calcula cuánto falta por pagar"""
        return self.valor_total - self.valor_pagado
    
    @property
    def porcentaje_pagado(self):
        """Calcula % pagado del total"""
        if self.valor_total > 0:
            return (self.valor_pagado / self.valor_total) * 100
        return 0


# ==================================================
# APU - ANÁLISIS DE PRECIO UNITARIO (NUEVO)
# ==================================================
class APU(models.Model):
    CATEGORIA_CHOICES = [
        ('closet_principal', 'Closet Alcoba Principal'),
        ('closet_auxiliar', 'Closet Alcoba Auxiliar'),
        ('cocina_integral', 'Cocina Integral'),
        ('mueble_bano', 'Mueble de Baño'),
        ('mueble_tv', 'Mueble de TV'),
        ('otro', 'Otro'),
    ]
    
    codigo = models.CharField("Código APU", max_length=50, unique=True)
    nombre = models.CharField("Nombre", max_length=200)
    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=CATEGORIA_CHOICES,
        default='otro'
    )
    descripcion = models.TextField("Descripción", blank=True)
    imagen = models.ImageField(
        "Imagen",
        upload_to='apu_imagenes/',
        null=True,
        blank=True
    )
    
    # Precio de venta
    factor_venta = models.DecimalField(
        "Factor de Venta",
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.80'),
        help_text="Multiplicador sobre el costo (ej: 1.80 = 80% de utilidad)"
    )
    
    # Control
    activo = models.BooleanField("Activo", default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='apus_creados'
    )
    
    class Meta:
        verbose_name = "APU"
        verbose_name_plural = "APUs"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def costo_materiales(self):
        """Suma de todos los materiales del APU"""
        return sum(
            item.costo_total 
            for item in self.materiales.all()
        )
    
    @property
    def costo_mano_obra(self):
        """Suma de toda la mano de obra"""
        return sum(
            mo.costo_total
            for mo in self.mano_obra.all()
        )
    
    @property
    def costo_total(self):
        """Costo total del APU"""
        return self.costo_materiales + self.costo_mano_obra
    
    @property
    def precio_venta(self):
        """Precio de venta calculado"""
        return self.costo_total * self.factor_venta


# ==================================================
# APU MATERIAL (NUEVO)
# ==================================================
class APUMaterial(models.Model):
    apu = models.ForeignKey(
        APU,
        on_delete=models.CASCADE,
        related_name='materiales',
        verbose_name='APU'
    )
    insumo = models.ForeignKey(
        'inventario.Insumo',
        on_delete=models.PROTECT,
        verbose_name='Insumo'
    )
    cantidad_requerida = models.DecimalField(
        "Cantidad Requerida",
        max_digits=10,
        decimal_places=3
    )
    precio_unitario = models.DecimalField(
        "Precio Unitario",
        max_digits=12,
        decimal_places=2,
        help_text="Precio snapshot del insumo al momento de crear el APU"
    )
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Material de APU"
        verbose_name_plural = "Materiales de APU"
        unique_together = ['apu', 'insumo']
    
    def __str__(self):
        return f"{self.insumo.nombre} × {self.cantidad_requerida}"
    
    @property
    def unidad(self):
        """Hereda la unidad del insumo"""
        return self.insumo.unidad
    
    @property
    def costo_total(self):
        """Costo total del material"""
        return self.cantidad_requerida * self.precio_unitario
    
    def save(self, *args, **kwargs):
        """Al guardar, toma el precio actual del insumo si no se especificó"""
        if not self.precio_unitario:
            self.precio_unitario = self.insumo.precio_unitario
        super().save(*args, **kwargs)


# ==================================================
# APU MANO DE OBRA (NUEVO)
# ==================================================
class APUManoObra(models.Model):
    TIPO_CHOICES = [
        ('fabrica', 'Fabricación en Taller'),
        ('instalacion', 'Instalación en Obra'),
    ]
    
    apu = models.ForeignKey(
        APU,
        on_delete=models.CASCADE,
        related_name='mano_obra',
        verbose_name='APU'
    )
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES)
    descripcion = models.CharField("Descripción", max_length=200)
    horas = models.DecimalField("Horas", max_digits=6, decimal_places=2)
    tarifa_hora = models.DecimalField(
        "Tarifa por Hora",
        max_digits=10,
        decimal_places=2
    )
    
    class Meta:
        verbose_name = "Mano de Obra de APU"
        verbose_name_plural = "Mano de Obra de APU"
    
    def __str__(self):
        return f"{self.descripcion} - {self.horas}h"
    
    @property
    def costo_total(self):
        """Costo total de la mano de obra"""
        return self.horas * self.tarifa_hora


# ==================================================
# COTIZACIÓN (NUEVO)
# ==================================================
class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='cotizaciones',
        verbose_name='Proyecto'
    )
    codigo = models.CharField("Código", max_length=50, unique=True)
    titulo = models.CharField("Título", max_length=200)
    descripcion = models.TextField("Descripción", blank=True)
    
    # Estado
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador'
    )
    
    # Fechas
    fecha_emision = models.DateField("Fecha de Emisión", default=timezone.now)
    fecha_validez = models.DateField("Fecha de Validez", null=True, blank=True)
    fecha_aprobacion = models.DateTimeField("Fecha de Aprobación", null=True, blank=True)
    aprobada_por = models.CharField("Aprobada Por", max_length=100, blank=True)
    
    # Montos
    descuento = models.DecimalField(
        "Descuento",
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Descuento en pesos o porcentaje"
    )
    
    # Control de órdenes de compra
    ordenes_generadas = models.BooleanField(
        "Órdenes de Compra Generadas",
        default=False
    )
    fecha_generacion_ordenes = models.DateTimeField(
        "Fecha Generación OCs",
        null=True,
        blank=True
    )
    
    # Observaciones
    observaciones = models.TextField("Observaciones", blank=True)
    
    # Auditoría
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cotizaciones_creadas'
    )
    
    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.codigo} - {self.titulo}"
    
    @property
    def subtotal(self):
        """Suma de todos los items"""
        return sum(item.valor_total for item in self.items.all())
    
    @property
    def total(self):
        """Total con descuento aplicado"""
        return self.subtotal - self.descuento
    
    def save(self, *args, **kwargs):
        """Generar código automático si no existe"""
        if not self.codigo:
            from datetime import datetime
            year = datetime.now().year
            last = Cotizacion.objects.filter(
                codigo__startswith=f'COT-{year}'
            ).order_by('-id').first()
            
            if last:
                last_num = int(last.codigo.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.codigo = f'COT-{year}-{new_num:03d}'
        
        super().save(*args, **kwargs)


# ==================================================
# ITEM COTIZACIÓN (NUEVO)
# ==================================================
class ItemCotizacion(models.Model):
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cotización'
    )
    apu = models.ForeignKey(
        APU,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='APU',
        help_text="Si se basa en un APU"
    )
    descripcion = models.CharField("Descripción", max_length=300)
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(
        "Precio Unitario",
        max_digits=12,
        decimal_places=2
    )
    orden = models.PositiveIntegerField("Orden", default=0)
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Item de Cotización"
        verbose_name_plural = "Items de Cotización"
        ordering = ['orden', 'id']
    
    def __str__(self):
        return f"{self.descripcion} × {self.cantidad}"
    
    @property
    def valor_total(self):
        """Valor total del item"""
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        """Si está basado en APU, tomar su precio"""
        if self.apu and not self.precio_unitario:
            self.precio_unitario = self.apu.precio_venta
        super().save(*args, **kwargs)


# ==================================================
# ITEM CONTRATADO (MODIFICAR - agregar campos)
# ==================================================
class ItemContratado(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Proyecto'
    )
    
    # 🆕 NUEVOS CAMPOS
    cotizacion = models.ForeignKey(
        'Cotizacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cotización Origen'
    )
    apu = models.ForeignKey(
        APU,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='APU'
    )
    insumo = models.ForeignKey(
        'inventario.Insumo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Insumo Relacionado'
    )
    
    # Campos básicos
    item = models.CharField("Item", max_length=200)
    cantidad = models.DecimalField("Cantidad", max_digits=10, decimal_places=2)
    unidad = models.CharField("Unidad", max_length=20, default="und")
    valor_unitario = models.DecimalField(
        "Valor Unitario",
        max_digits=12,
        decimal_places=2
    )
    es_manual = models.BooleanField("Es Manual", default=False)
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Item Contratado"
        verbose_name_plural = "Items Contratados"
    
    def __str__(self):
        return f"{self.item} × {self.cantidad}"
    
    @property
    def valor_total(self):
        """Valor total del item"""
        return self.cantidad * self.valor_unitario


# ==================================================
# ANTICIPO (NUEVO)
# ==================================================
class Anticipo(models.Model):
    TIPO_CHOICES = [
        ('anticipo_inicial', 'Anticipo Inicial'),
        ('corte_1', 'Corte 1'),
        ('corte_2', 'Corte 2'),
        ('corte_3', 'Corte 3'),
        ('liquidacion', 'Liquidación Final'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('recibido', 'Recibido'),
        ('aplicado', 'Aplicado al Proyecto'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='anticipos',
        verbose_name='Proyecto'
    )
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES)
    porcentaje = models.DecimalField(
        "Porcentaje",
        max_digits=5,
        decimal_places=2,
        help_text="% del valor total del proyecto"
    )
    monto = models.DecimalField(
        "Monto",
        max_digits=15,
        decimal_places=2
    )
    condicion = models.CharField(
        "Condición",
        max_length=200,
        blank=True,
        help_text="Ej: Al 40% de avance"
    )
    
    # Estado
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    fecha_esperada = models.DateField("Fecha Esperada", null=True, blank=True)
    fecha_recibido = models.DateField("Fecha Recibido", null=True, blank=True)
    comprobante = models.FileField(
        "Comprobante",
        upload_to='anticipos/',
        null=True,
        blank=True
    )
    
    observaciones = models.TextField("Observaciones", blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Anticipo"
        verbose_name_plural = "Anticipos"
        ordering = ['proyecto', 'tipo']
    
    def __str__(self):
        return f"{self.proyecto.codigo} - {self.get_tipo_display()}: ${self.monto:,.0f}"


# ==================================================
# PRESUPUESTO DE COMPRAS (NUEVO)
# ==================================================
class PresupuestoCompras(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='presupuestos_compras',
        verbose_name='Proyecto'
    )
    
    # Presupuesto
    anticipo_base = models.DecimalField(
        "Anticipo Base",
        max_digits=15,
        decimal_places=2,
        help_text="Monto del anticipo recibido"
    )
    porcentaje_asignado = models.DecimalField(
        "Porcentaje Asignado",
        max_digits=5,
        decimal_places=2,
        default=80,
        help_text="% del anticipo destinado a compras"
    )
    monto_asignado = models.DecimalField(
        "Monto Asignado",
        max_digits=15,
        decimal_places=2,
        editable=False
    )
    
    # Control en tiempo real
    monto_disponible = models.DecimalField(
        "Monto Disponible",
        max_digits=15,
        decimal_places=2
    )
    monto_comprometido = models.DecimalField(
        "Monto Comprometido",
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="OCs pendientes de ejecutar"
    )
    monto_ejecutado = models.DecimalField(
        "Monto Ejecutado",
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="OCs ya pagadas"
    )
    
    # Auditoría
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Asignado Por'
    )
    fecha_asignacion = models.DateTimeField("Fecha de Asignación", auto_now_add=True)
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Presupuesto de Compras"
        verbose_name_plural = "Presupuestos de Compras"
    
    def __str__(self):
        return f"Presupuesto {self.proyecto.codigo}: ${self.monto_asignado:,.0f}"
    
    @property
    def monto_libre(self):
        """Monto disponible menos comprometido"""
        return self.monto_disponible - self.monto_comprometido
    
    @property
    def porcentaje_usado(self):
        """% del presupuesto ya ejecutado"""
        if self.monto_asignado > 0:
            return (self.monto_ejecutado / self.monto_asignado) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Calcular monto asignado automáticamente"""
        self.monto_asignado = (self.anticipo_base * self.porcentaje_asignado) / 100
        if not self.pk:  # Si es nuevo
            self.monto_disponible = self.monto_asignado
        super().save(*args, **kwargs)


# ==================================================
# ENTREGA PROGRAMADA (NUEVO)
# ==================================================
class EntregaProgramada(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_produccion', 'En Producción'),
        ('lista', 'Lista para Despacho'),
        ('despachada', 'Despachada'),
        ('cerrada', 'Cerrada'),
    ]
    
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name='Proyecto'
    )
    numero_entrega = models.PositiveIntegerField("Número de Entrega")
    fecha_requerida = models.DateField("Fecha Requerida por Cliente")
    fecha_real = models.DateField("Fecha Real de Entrega", null=True, blank=True)
    
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    observaciones = models.TextField("Observaciones", blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Entrega Programada"
        verbose_name_plural = "Entregas Programadas"
        unique_together = ['proyecto', 'numero_entrega']
        ordering = ['proyecto', 'numero_entrega']
    
    def __str__(self):
        return f"{self.proyecto.codigo} - Entrega #{self.numero_entrega}"
    
    @property
    def porcentaje_avance(self):
        """% de avance según OTs completadas"""
        from nexusone.administrativa.ordenes.models import OrdenTrabajo
        
        ots = OrdenTrabajo.objects.filter(entrega_programada=self)
        total = ots.count()
        if total == 0:
            return 0
        
        cerradas = ots.filter(estado='cerrada').count()
        return (cerradas / total) * 100
    
    @property
    def esta_atrasada(self):
        """Verifica si está atrasada"""
        from django.utils import timezone
        if self.estado in ['despachada', 'cerrada']:
            return False
        return timezone.now().date() > self.fecha_requerida


# ==================================================
# ITEM ENTREGA (NUEVO)
# ==================================================
class ItemEntrega(models.Model):
    entrega = models.ForeignKey(
        EntregaProgramada,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Entrega'
    )
    item_contratado = models.ForeignKey(
        ItemContratado,
        on_delete=models.CASCADE,
        verbose_name='Item Contratado'
    )
    cantidad = models.DecimalField(
        "Cantidad",
        max_digits=10,
        decimal_places=2
    )
    
    # Control de producción
    cantidad_producida = models.DecimalField(
        "Cantidad Producida",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    cantidad_despachada = models.DecimalField(
        "Cantidad Despachada",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    class Meta:
        verbose_name = "Item de Entrega"
        verbose_name_plural = "Items de Entrega"
        unique_together = ['entrega', 'item_contratado']
    
    def __str__(self):
        return f"{self.item_contratado.item} × {self.cantidad}"
    
    @property
    def porcentaje_produccion(self):
        """% de producción completada"""
        if self.cantidad > 0:
            return (self.cantidad_producida / self.cantidad) * 100
        return 0
    
    @property
    def porcentaje_despacho(self):
        """% despachado"""
        if self.cantidad > 0:
            return (self.cantidad_despachada / self.cantidad) * 100
        return 0