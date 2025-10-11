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
        ('la_riviera', 'La Riviera'),
        ('maca', 'Maca'),
        ('torreon', 'Torreon'),
        ('c_u', 'C&U'),
        ('plinco', 'Plinco'),
        ('urbana', 'Urbana'),
        ('N/E', 'N/E'),
    ]
    PROYECTO_CHOICES = [
        ('ventura', 'Ventura'),
        ('la_primavera', 'La Primavera'),
        ('mallorca', 'Mallorca'),
        ('o2_del_cerro', 'O2 del Cerro'),
        ('antigua', 'Antigua'),
        ('Cocinas Pereira', 'Cocinas Pereira'),
        ('externo', 'Externo'),
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

    numero = models.CharField("Número OT", max_length=5, unique=True, default=generar_numero_ot)
    descripcion = models.TextField("Descripción", blank=True)
    constructora = models.CharField("Constructora", max_length=40, choices=CONSTRUCTORA_CHOICES)
    proyecto = models.CharField("Proyecto", max_length=40, choices=PROYECTO_CHOICES)
    proceso = models.CharField("Proceso", max_length=20, choices=PROCESO_CHOICES)
    fecha_apertura = models.DateTimeField("Fecha de Apertura", auto_now_add=True, null=True, blank=True)
    fecha_envio = models.DateField("Fecha de Envío", null=True, blank=True)
    estado = models.CharField("Estado", max_length=20, choices=ESTADO_CHOICES, default='abierta')
    fecha_cierre = models.DateField("Fecha de Cierre", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OT {self.numero} — {self.get_constructora_display()} / {self.get_proyecto_display()}"

    def cerrar(self):
        if self.estado != "cerrada":
            self.estado = "cerrada"
            self.fecha_cierre = timezone.now()
            self.save()


def ruta_documento_ot(instance, filename):
    """
    Define la ruta dentro de MEDIA_ROOT donde se almacenarán los archivos.
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

    # ✅ Eliminamos campos de Google Drive (ya no son necesarios)
    # Mantiene compatibilidad con templates y forms antiguos
    drive_file_id = models.CharField(max_length=255, blank=True, null=True)
    drive_view_url = models.URLField(blank=True, null=True)
    drive_download_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre or (self.archivo.name if self.archivo else "Documento")
