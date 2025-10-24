from django.db import models
from django.core.validators import RegexValidator


# ===================================
# 🏢 CONSTRUCTORA
# ===================================
class Constructora(models.Model):
    razon_social = models.CharField(
        "Razón Social", 
        max_length=200, 
        unique=True,
        help_text="Nombre legal de la constructora"
    )
    
    nit = models.CharField(
        "NIT", 
        max_length=20, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{9,10}-\d{1}$',
                message='Formato de NIT inválido. Debe ser: 123456789-0'
            )
        ],
        help_text="Formato: 123456789-0"
    )
    
    telefono = models.CharField(
        "Teléfono", 
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s-]{7,15}$',
                message='Número de teléfono inválido'
            )
        ],
        help_text="Ej: +57 311 1234567"
    )
    
    ubicacion = models.CharField(
        "Ubicación", 
        max_length=300,
        help_text="Dirección de oficina principal"
    )
    
    correo = models.EmailField(
        "Correo Electrónico",
        help_text="Email de contacto principal"
    )
    
    # Campos adicionales útiles
    representante_legal = models.CharField(
        "Representante Legal", 
        max_length=150,
        blank=True,
        help_text="Nombre del representante legal"
    )
    
    contacto_adicional = models.TextField(
        "Información de Contacto Adicional",
        blank=True,
        help_text="Otros teléfonos, emails o contactos importantes"
    )
    
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
        help_text="Notas generales sobre la constructora"
    )
    
    # Control
    activa = models.BooleanField("Constructora Activa", default=True)
    creado = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    actualizado = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Constructora"
        verbose_name_plural = "Constructoras"
        ordering = ['razon_social']
    
    def __str__(self):
        return self.razon_social
    
    @property
    def total_proyectos(self):
        """Retorna el número total de proyectos"""
        return self.proyectos.count()
    
    @property
    def proyectos_activos(self):
        """Retorna el número de proyectos activos"""
        return self.proyectos.filter(estado='en_curso').count()


# ===================================
# 🏗️ PROYECTO
# ===================================
class Proyecto(models.Model):
    TIPO_PROYECTO_CHOICES = [
        ('vis', 'VIS - Vivienda de Interés Social'),
        ('vip', 'VIP - Vivienda de Interés Prioritario'),
        ('apto_modelo', 'Apartamento Modelo'),
        ('casa', 'Casa'),
        ('apartamentos', 'Apartamentos'),
        ('secciones', 'Secciones'),
        ('torre_1', 'Torre 1'),
        ('torre_2', 'Torre 2'),
        ('torre_3', 'Torre 3'),
        ('torre_4', 'Torre 4'),
        ('ala_a', 'Ala A'),
        ('ala_b', 'Ala B'),
        ('etapa_1', 'Etapa 1'),
        ('etapa_2', 'Etapa 2'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('planeacion', 'Planeación'),
        ('en_curso', 'En Curso'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Relación con Constructora
    constructora = models.ForeignKey(
        Constructora,
        on_delete=models.CASCADE,
        related_name='proyectos',
        verbose_name='Constructora'
    )
    
    # Información básica del proyecto
    nombre = models.CharField(
        "Nombre del Proyecto", 
        max_length=200,
        help_text="Nombre descriptivo del proyecto"
    )
    
    tipo_proyecto = models.CharField(
        "Tipo de Proyecto",
        max_length=20,
        choices=TIPO_PROYECTO_CHOICES,
        default='apartamentos'
    )
    
    codigo = models.CharField(
        "Código del Proyecto",
        max_length=50,
        unique=True,
        help_text="Código único de identificación (ej: PROJ-2025-001)"
    )
    
    # Ubicación del proyecto
    ubicacion_proyecto = models.CharField(
        "Ubicación del Proyecto",
        max_length=300,
        help_text="Dirección donde se ejecuta el proyecto"
    )
    
    # Contrato
    contrato = models.FileField(
        "Contrato (PDF)",
        upload_to='contratos/',
        null=True,
        blank=True,
        help_text="Archivo PDF del contrato"
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        "Fecha de Inicio",
        null=True,
        blank=True
    )
    
    fecha_fin_estimada = models.DateField(
        "Fecha de Finalización Estimada",
        null=True,
        blank=True
    )
    
    fecha_fin_real = models.DateField(
        "Fecha de Finalización Real",
        null=True,
        blank=True,
        help_text="Fecha real de finalización del proyecto"
    )
    
    # Estado y presupuesto
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADO_CHOICES,
        default='planeacion'
    )
    
    presupuesto = models.DecimalField(
        "Presupuesto",
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Presupuesto total del proyecto"
    )
    
    # Información adicional
    descripcion = models.TextField(
        "Descripción",
        blank=True,
        help_text="Descripción detallada del proyecto"
    )
    
    numero_unidades = models.PositiveIntegerField(
        "Número de Unidades",
        null=True,
        blank=True,
        help_text="Cantidad de apartamentos, casas, etc."
    )
    
    observaciones = models.TextField(
        "Observaciones",
        blank=True,
        help_text="Notas adicionales sobre el proyecto"
    )
    
    # Control
    activo = models.BooleanField("Proyecto Activo", default=True)
    creado = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    actualizado = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.constructora.razon_social})"
    
    @property
    def duracion_dias(self):
        """Calcula la duración del proyecto en días"""
        if self.fecha_inicio and self.fecha_fin_estimada:
            return (self.fecha_fin_estimada - self.fecha_inicio).days
        return None
    
    @property
    def dias_transcurridos(self):
        """Calcula los días transcurridos desde el inicio"""
        if self.fecha_inicio:
            from datetime import date
            return (date.today() - self.fecha_inicio).days
        return None
    
    @property
    def porcentaje_tiempo(self):
        """Calcula el porcentaje de tiempo transcurrido"""
        if self.duracion_dias and self.dias_transcurridos and self.duracion_dias > 0:
            porcentaje = (self.dias_transcurridos / self.duracion_dias) * 100
            return min(porcentaje, 100)  # No más del 100%
        return None
    @property
    def presupuesto_calculado(self):
        """Calcula el presupuesto total sumando todos los ítems contratados"""
        total = sum(item.valor_total for item in self.items_contratados.all())
        return total if total > 0 else None


# ===================================
# 📋 ITEM CONTRATADO
# ===================================
class ItemContratado(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='items_contratados',
        verbose_name='Proyecto'
    )
    
    item = models.CharField(
        "Item",
        max_length=200,
        help_text="Nombre del ítem contratado"
    )
    
    medida = models.CharField(
        "Unidad de Medida",
        max_length=50,
        help_text="Ej: m², m³, unidad, kg, etc."
    )
    
    cantidad = models.DecimalField(
        "Cantidad",
        max_digits=10,
        decimal_places=2,
        help_text="Cantidad contratada"
    )
    
    valor_unitario = models.DecimalField(
        "Valor Unitario",
        max_digits=15,
        decimal_places=2,
        help_text="Valor por unidad"
    )
    
    # Campos de control
    creado = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    actualizado = models.DateTimeField("Última Actualización", auto_now=True)
    
    class Meta:
        verbose_name = "Item Contratado"
        verbose_name_plural = "Items Contratados"
        ordering = ['creado']
    
    def __str__(self):
        return f"{self.item} - {self.cantidad} {self.medida}"
    
    @property
    def valor_total(self):
        """Calcula el valor total del ítem (cantidad * valor_unitario)"""
        return self.cantidad * self.valor_unitario