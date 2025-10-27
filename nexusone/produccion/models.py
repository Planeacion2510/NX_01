# nexusone/produccion/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Importar OrdenTrabajo desde administrativa
from nexusone.administrativa.ordenes.models import OrdenTrabajo


# ==================================================
# AVANCE DE PRODUCCIÓN
# ==================================================
class AvanceProduccion(models.Model):
    """
    Registro de avances en una Orden de Trabajo
    Usado por el módulo de producción para llevar control
    """
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='avances',
        verbose_name='Orden de Trabajo'
    )
    fecha_registro = models.DateTimeField(
        "Fecha de Registro",
        auto_now_add=True
    )
    cantidad_avance = models.DecimalField(
        "Cantidad en este Avance",
        max_digits=10,
        decimal_places=2,
        help_text="Cantidad producida en este registro"
    )
    cantidad_acumulada = models.DecimalField(
        "Cantidad Acumulada",
        max_digits=10,
        decimal_places=2,
        help_text="Total acumulado hasta este avance"
    )
    
    # Quién registra
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Registrado Por'
    )
    
    # Detalles
    observaciones = models.TextField("Observaciones", blank=True)
    evidencia = models.ImageField(
        "Evidencia Fotográfica",
        upload_to='produccion/avances/',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Avance de Producción"
        verbose_name_plural = "Avances de Producción"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"OT-{self.orden.numero}: +{self.cantidad_avance} ({self.fecha_registro.strftime('%d/%m/%Y %H:%M')})"
    
    def save(self, *args, **kwargs):
        """Al guardar, actualizar la cantidad producida en la OT"""
        # Si es un nuevo registro
        if not self.pk:
            # Calcular cantidad acumulada
            ultimo_avance = AvanceProduccion.objects.filter(
                orden=self.orden
            ).order_by('-fecha_registro').first()
            
            if ultimo_avance:
                self.cantidad_acumulada = ultimo_avance.cantidad_acumulada + self.cantidad_avance
            else:
                self.cantidad_acumulada = self.cantidad_avance
        
        super().save(*args, **kwargs)
        
        # Actualizar la OT
        self.orden.cantidad_producida = self.cantidad_acumulada
        self.orden.save(update_fields=['cantidad_producida'])


# ==================================================
# ASIGNACIÓN DE OPERARIO
# ==================================================
class AsignacionOperario(models.Model):
    """
    Asigna operarios específicos a órdenes de trabajo
    """
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Orden de Trabajo'
    )
    operario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ordenes_asignadas_produccion',
        verbose_name='Operario'
    )
    fecha_asignacion = models.DateTimeField(
        "Fecha de Asignación",
        auto_now_add=True
    )
    fecha_finalizacion = models.DateTimeField(
        "Fecha de Finalización",
        null=True,
        blank=True
    )
    
    activo = models.BooleanField("Activo", default=True)
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Asignación de Operario"
        verbose_name_plural = "Asignaciones de Operarios"
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"OT-{self.orden.numero} → {self.operario.get_full_name() or self.operario.username}"
    
    def finalizar(self):
        """Marca la asignación como finalizada"""
        self.activo = False
        self.fecha_finalizacion = timezone.now()
        self.save()


# ==================================================
# MATERIAL DE ORDEN (Control de materiales)
# ==================================================
class MaterialOrden(models.Model):
    """
    Control de materiales requeridos y utilizados por cada OT
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignado', 'Asignado'),
        ('consumido', 'Consumido'),
    ]
    
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='materiales',
        verbose_name='Orden de Trabajo'
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
    cantidad_asignada = models.DecimalField(
        "Cantidad Asignada",
        max_digits=10,
        decimal_places=3,
        default=0
    )
    cantidad_utilizada = models.DecimalField(
        "Cantidad Utilizada",
        max_digits=10,
        decimal_places=3,
        default=0
    )
    
    estado = models.CharField(
        "Estado",
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    
    fecha_asignacion = models.DateTimeField(
        "Fecha de Asignación",
        null=True,
        blank=True
    )
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Asignado Por'
    )
    
    observaciones = models.TextField("Observaciones", blank=True)
    
    class Meta:
        verbose_name = "Material de Orden"
        verbose_name_plural = "Materiales de Órdenes"
        unique_together = ['orden', 'insumo']
    
    def __str__(self):
        return f"OT-{self.orden.numero}: {self.insumo.nombre} ({self.cantidad_requerida} {self.insumo.unidad})"
    
    @property
    def cantidad_faltante(self):
        """Cantidad que falta por asignar"""
        return self.cantidad_requerida - self.cantidad_asignada
    
    @property
    def porcentaje_asignado(self):
        """% del material ya asignado"""
        if self.cantidad_requerida > 0:
            return (self.cantidad_asignada / self.cantidad_requerida) * 100
        return 0
    
    def asignar_material(self, cantidad, usuario):
        """Asigna material del inventario a esta OT"""
        if cantidad > self.cantidad_faltante:
            raise ValueError("No se puede asignar más de lo requerido")
        
        # Verificar stock disponible
        if self.insumo.stock_actual < cantidad:
            raise ValueError("Stock insuficiente en inventario")
        
        # Crear movimiento de salida en el kardex
        from nexusone.administrativa.inventario.models import MovimientoKardex
        MovimientoKardex.objects.create(
            insumo=self.insumo,
            tipo='salida',
            cantidad=int(cantidad),
            observacion=f'Asignado a OT-{self.orden.numero}',
            fecha=timezone.now()
        )
        
        # Actualizar asignación
        self.cantidad_asignada += cantidad
        self.estado = 'asignado' if self.cantidad_asignada >= self.cantidad_requerida else 'pendiente'
        self.fecha_asignacion = timezone.now()
        self.asignado_por = usuario
        self.save()


# ==================================================
# PAUSA DE PRODUCCIÓN
# ==================================================
class PausaProduccion(models.Model):
    """
    Registro de pausas en la producción de una OT
    """
    MOTIVO_CHOICES = [
        ('falta_material', 'Falta de Material'),
        ('mantenimiento', 'Mantenimiento de Maquinaria'),
        ('problema_tecnico', 'Problema Técnico'),
        ('cambio_prioridad', 'Cambio de Prioridad'),
        ('otro', 'Otro'),
    ]
    
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='pausas',
        verbose_name='Orden de Trabajo'
    )
    motivo = models.CharField("Motivo", max_length=30, choices=MOTIVO_CHOICES)
    descripcion = models.TextField("Descripción del Motivo")
    
    fecha_inicio = models.DateTimeField("Fecha de Inicio", auto_now_add=True)
    fecha_fin = models.DateTimeField("Fecha de Fin", null=True, blank=True)
    
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Registrado Por'
    )
    
    activa = models.BooleanField("Activa", default=True)
    
    class Meta:
        verbose_name = "Pausa de Producción"
        verbose_name_plural = "Pausas de Producción"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"OT-{self.orden.numero}: {self.get_motivo_display()}"
    
    @property
    def duracion(self):
        """Duración de la pausa"""
        if self.fecha_fin:
            return self.fecha_fin - self.fecha_inicio
        else:
            return timezone.now() - self.fecha_inicio
    
    def finalizar(self):
        """Finaliza la pausa"""
        self.activa = False
        self.fecha_fin = timezone.now()
        self.save()
        
        # Cambiar estado de la OT de 'pausada' a 'en_proceso'
        if self.orden.estado == 'pausada':
            self.orden.estado = 'en_proceso'
            self.orden.save(update_fields=['estado'])