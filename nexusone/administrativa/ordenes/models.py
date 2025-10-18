# nexusone/administrativa/ordenes/models.py
from django.db import models
from django.utils import timezone
import os


def generar_numero_ot():
    ultimo = OrdenTrabajo.objects.order_by("-id").first()
    if not ultimo:
        return "00001"
    try:
        ultimo_num = int(ultimo.numero)
    except Exception:
        ultimo_num = 0
    nuevo_num = str(ultimo_num + 1).zfill(5)
    return nuevo_num


class OrdenTrabajo(models.Model):
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
        ('abierta', 'Abierta'),
        ('en_proceso', 'En proceso'),
        ('cerrada', 'Cerrada'),
    ]

    numero = models.CharField("NÃºmero OT", max_length=5, unique=True, default=generar_numero_ot)
    descripcion = models.TextField("DescripciÃ³n", blank=True)
    constructora = models.CharField("Constructora", max_length=40, choices=CONSTRUCTORA_CHOICES)
    proyecto = models.CharField("Proyecto", max_length=40, choices=PROYECTO_CHOICES)
    proceso = models.CharField("Proceso", max_length=20, choices=PROCESO_CHOICES)
    fecha_apertura = models.DateTimeField("Fecha de Apertura", auto_now_add=True, null=True, blank=True)
    fecha_envio = models.DateField("Fecha de EnvÃ­o", null=True, blank=True)
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default='abierta')
    fecha_cierre = models.DateTimeField("Fecha de Cierre", null=True, blank=True)  # âœ… Cambiado a DateTimeField
    cierre_a_tiempo = models.BooleanField("Cierre a Tiempo", null=True, blank=True)  # âœ… NUEVO CAMPO
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OT {self.numero} â€” {self.get_constructora_display()} / {self.get_proyecto_display()}"

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


def ruta_documento_ot(instance, filename):
    """
    Define la ruta dentro de MEDIA_ROOT donde se almacenarÃ¡n los archivos.
    Estructura:
    Ordenes/<numero_ot>/<tipo_archivo>/<nombre_archivo>
    """
    extension = filename.split(".")[-1].lower()
    if extension in ["jpg", "jpeg", "png", "gif"]:
        subcarpeta = "evidencias"
    elif extension in ["pdf", "doc", "docx", "xlsx", "xls"]:
        subcarpeta = "documentos"
    else:
        subcarpeta = "otros"

    # Carpeta final: Ordenes/<numero_ot>/<subcarpeta>/
    return os.path.join("Ordenes", instance.orden.numero, subcarpeta, filename)


class DocumentoOrden(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, related_name="documentos", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, default="Documento sin nombre")
    archivo = models.FileField(upload_to=ruta_documento_ot, blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre or (self.archivo.name if self.archivo else "Documento")

# Agregar al final de tu models.py existente

from django.contrib.auth.models import User

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('nueva_orden', 'Nueva Orden'),
        ('proxima_envio', 'Próxima a Envío'),
        ('vencida', 'Orden Vencida'),
        ('a_tiempo', 'Cerrada a Tiempo'),
        ('tarde', 'Cerrada Tarde'),
    ]
    
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.tipo} - {self.orden.numero}"