# nexusone/administrativa/ordenes/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os


def generar_numero_ot():
    """Genera el siguiente número de OT disponible"""
    ultimo = OrdenTrabajo.objects.order_by("-id").first()
    if not ultimo:
        return "00001"
    try:
        ultimo_num = int(ultimo.numero)
    except Exception:
        ultimo_num = 0
    nuevo_num = str(ultimo_num + 1).zfill(5)
    return nuevo_num


# ==================================================
# ORDEN DE TRABAJO (MODIFICADA - Con nuevos campos)
# ==================================================
class OrdenTrabajo(models.Model):
    # Choices existentes (mantener para compatibilidad)
    CONSTRUCTORA_CHOICES = [
        ('consorcio_alfa', 'Consorcio Alfa'),
        ('asul', 'Asul'),
        ('maca', 'Maca'),
        ('torreon', 'Torreon'),
        ('c_u', 'C&U'),
        ('plinco', 'Plinco'),
        ('nucleo', 'Nucleo'),
        ('urbana', 'Urbana'),
        ('N/E', 'N/E'),
    ]
    
    PROYECTO_CHOICES = [
        ('ventura', 'Ventura'),
        ('la_primavera', 'La Primavera'),
        ('mallorca', 'Mallorca'),
        ('o2_del_cerro', 'O2 del Cerro'),
        ('antigua', 'Antigua'),
        ('montreal', 'MontReal'),
        ('koa', 'Koa Loft'),
        ('perla nova', 'Perla Nova'),
        ('riviera verde', 'Riviera Verde Etp 1'),
        ('Cocinas Pereira', 'Cocinas Pereira'),
        ('externo', 'Externo'),
        ('sala de ventas', 'Sala de Ventas'),
        ('apto modelo', 'Apto Modelo'),
    ]
    
    PROCESO_CHOICES = [
        ('mecanizado', 'Mecanizado'),
        ('ensamble', 'Ensamble'),
        ('despacho', 'Despacho'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),        # Esperando dependencia
        ('abierta', 'Abierta'),            # Lista para iniciar
        ('en_proceso', 'En proceso'),      # En producción
        ('pausada', 'Pausada'),            # Temporalmente detenida
        ('cerrada', 'Cerrada'),            # Completada
    ]
    
    ORIGEN_CHOICES = [
        ('manual', 'Manual'),
        ('automatica', 'Automática'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # ═══════════════════════════════════════════════
    # CAMPOS BÁSICOS (existentes)
    # ═══════════════════════════════════════════════
    numero = models.CharField(
        "Número OT",
        max_length=5,
        unique=True,
        default=generar_numero_ot
    )
    descripcion = models.TextField("Descripción", blank=True)
    
    # Campos legacy (mantener para OTs manuales y compatibilidad)
    constructora = models.CharField(
        "Constructora",
        max_length=40,
        choices=CONSTRUCTORA_CHOICES,
        blank=True
    )
    proyecto = models.CharField(
        "Proyecto",
        max_length=40,
        choices=PROYECTO_CHOICES,
        blank=True
    )
    
    proceso = models.CharField("Proceso", max_length=20, choices=PROCESO_CHOICES)
    
    # Fechas existentes
    fecha_apertura = models.DateTimeField(
        "Fecha de Apertura",
        auto_now_add=True,
        null=True,
        blank=True
    )
    fecha_envio = models.DateField("Fecha de Envío", null=True, blank=True)
    fecha_cierre = models.DateTimeField("Fecha de Cierre", null=True, blank=True)
    
    # Control existente
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='abierta'
    )
    cierre_a_tiempo = models.BooleanField("Cierre a Tiempo", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════
    # 🆕 NUEVOS CAMPOS
    # ═══════════════════════════════════════════════
    
    # Origen de la OT
    origen = models.CharField(
        "Origen",
        max_length=15,
        choices=ORIGEN_CHOICES,
        default='manual',
        help_text="Manual: creada por usuario. Automática: generada por el sistema"
    )
    
    # Vinculación a proyectos (para OTs automáticas)
    proyecto_fk = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_trabajo',
        verbose_name='Proyecto Vinculado'
    )
    entrega_programada = models.ForeignKey(
        'proyectos.EntregaProgramada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_trabajo',
        verbose_name='Entrega Programada'
    )
    item_contratado = models.ForeignKey(
        'proyectos.ItemContratado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_trabajo',
        verbose_name='Item Contratado'
    )
    
    # Control de producción
    cantidad_producir = models.DecimalField(
        "Cantidad a Producir",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cantidad total a producir (solo para OTs automáticas)"
    )
    cantidad_producida = models.DecimalField(
        "Cantidad Producida",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Workflow de dependencias
    orden_dependiente = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_dependientes_de_esta',
        verbose_name='Depende de OT'
    )
    
    # Asignación
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_asignadas',
        verbose_name='Responsable'
    )
    prioridad = models.CharField(
        "Prioridad",
        max_length=10,
        choices=PRIORIDAD_CHOICES,
        default='media'
    )
    
    # Fechas adicionales
    fecha_inicio_real = models.DateTimeField(
        "Fecha Inicio Real",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_apertura']
    
    def __str__(self):
        if self.proyecto_fk:
            return f"OT {self.numero} — {self.proyecto_fk.nombre}"
        elif self.proyecto:
            return f"OT {self.numero} — {self.get_proyecto_display()}"
        else:
            return f"OT {self.numero} — {self.descripcion[:50]}"
    
    # ═══════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════
    
    @property
    def porcentaje_avance(self):
        """Calcula el % de avance de producción"""
        if not self.cantidad_producir or self.cantidad_producir == 0:
            return 0
        return (self.cantidad_producida / self.cantidad_producir) * 100
    
    @property
    def dependencia_cumplida(self):
        """Verifica si la dependencia está cumplida"""
        if not self.orden_dependiente:
            return True
        return self.orden_dependiente.estado == 'cerrada'
    
    @property
    def puede_iniciar(self):
        """Verifica si puede iniciarse (dependencia cumplida y estado correcto)"""
        return self.dependencia_cumplida and self.estado in ['pendiente', 'abierta']
    
    @property
    def esta_atrasada(self):
        """Verifica si está atrasada"""
        if not self.fecha_envio or self.estado == 'cerrada':
            return False
        return timezone.now().date() > self.fecha_envio
    
    @property
    def dias_restantes(self):
        """Días restantes hasta la fecha de envío"""
        if not self.fecha_envio or self.estado == 'cerrada':
            return None
        delta = self.fecha_envio - timezone.now().date()
        return delta.days
    
    # ═══════════════════════════════════════════════
    # MÉTODOS
    # ═══════════════════════════════════════════════
    
    def cerrar(self):
        """Cierra la orden y calcula si fue a tiempo"""
        if self.estado != "cerrada":
            self.estado = "cerrada"
            self.fecha_cierre = timezone.now()
            
            # Calcular si el cierre fue a tiempo
            if self.fecha_envio:
                fecha_cierre_solo_fecha = self.fecha_cierre.date()
                if fecha_cierre_solo_fecha <= self.fecha_envio:
                    self.cierre_a_tiempo = True
                else:
                    self.cierre_a_tiempo = False
            
            self.save()


# ==================================================
# DOCUMENTO ORDEN (sin cambios)
# ==================================================
def ruta_documento_ot(instance, filename):
    """Define la ruta de almacenamiento de documentos"""
    extension = filename.split(".")[-1].lower()
    if extension in ["jpg", "jpeg", "png", "gif"]:
        subcarpeta = "evidencias"
    elif extension in ["pdf", "doc", "docx", "xlsx", "xls"]:
        subcarpeta = "documentos"
    else:
        subcarpeta = "otros"
    
    return os.path.join("Ordenes", instance.orden.numero, subcarpeta, filename)


class DocumentoOrden(models.Model):
    orden = models.ForeignKey(
        OrdenTrabajo,
        related_name="documentos",
        on_delete=models.CASCADE
    )
    nombre = models.CharField(max_length=255, default="Documento sin nombre")
    archivo = models.FileField(upload_to=ruta_documento_ot, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Documento de Orden"
        verbose_name_plural = "Documentos de Órdenes"
    
    def __str__(self):
        return self.nombre or (self.archivo.name if self.archivo else "Documento")


# ==================================================
# NOTIFICACIÓN (sin cambios)
# ==================================================
class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('nueva_orden', 'Nueva Orden'),
        ('proxima_envio', 'Próxima a Envío'),
        ('vencida', 'Orden Vencida'),
        ('a_tiempo', 'Cerrada a Tiempo'),
        ('tarde', 'Cerrada Tarde'),
    ]
    
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.tipo} - {self.orden.numero}"