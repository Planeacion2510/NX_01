from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta

# ============================================================================
# 1. ADMINISTRACIÓN DE PERSONAL
# ============================================================================

class Empleado(models.Model):
    """Modelo principal de empleados"""
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'En Vacaciones'),
        ('incapacidad', 'Incapacitado'),
        ('suspendido', 'Suspendido'),
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        ('union_libre', 'Unión Libre'),
        ('divorciado', 'Divorciado(a)'),
        ('viudo', 'Viudo(a)'),
    ]
    
    # Relación con usuario
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado', null=True, blank=True)
    
    # Información personal
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name='Número de documento')
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    lugar_expedicion = models.CharField(max_length=100, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True)
    
    # Contacto
    celular = models.CharField(max_length=20)
    telefono_fijo = models.CharField(max_length=20, blank=True)
    email_personal = models.EmailField(blank=True)
    email_corporativo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100, blank=True)
    
    # Contacto de emergencia
    contacto_emergencia_nombre = models.CharField(max_length=100, blank=True)
    contacto_emergencia_parentesco = models.CharField(max_length=50, blank=True)
    contacto_emergencia_telefono = models.CharField(max_length=20, blank=True)
    
    # Información laboral
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    jefe_inmediato = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinados')
    sede = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    
    # Salario (básico, sin prestaciones)
    salario_basico = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aplica_auxilio_transporte = models.BooleanField(default=True)
    salario_integral = models.BooleanField(default=False)
    
    # Seguridad Social
    eps = models.ForeignKey('EPS', on_delete=models.SET_NULL, null=True, blank=True)
    afp = models.ForeignKey('AFP', on_delete=models.SET_NULL, null=True, blank=True)
    arl = models.ForeignKey('ARL', on_delete=models.SET_NULL, null=True, blank=True)
    caja_compensacion = models.ForeignKey('CajaCompensacion', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información bancaria
    banco = models.CharField(max_length=100, blank=True)
    tipo_cuenta = models.CharField(max_length=20, choices=[('ahorros', 'Ahorros'), ('corriente', 'Corriente')], blank=True)
    numero_cuenta = models.CharField(max_length=20, blank=True)
    
    # Metadata
    foto = models.ImageField(upload_to='empleados/fotos/', null=True, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['-fecha_ingreso']
        
    def __str__(self):
        return self.get_nombre_completo()
    
    def get_nombre_completo(self):
        nombres = f"{self.primer_nombre} {self.segundo_nombre}".strip()
        apellidos = f"{self.primer_apellido} {self.segundo_apellido}".strip()
        return f"{nombres} {apellidos}".strip()
    
    def get_antiguedad(self):
        """Calcula la antigüedad en años, meses y días"""
        if not self.fecha_ingreso:
            return "N/A"
        
        hoy = date.today()
        delta = hoy - self.fecha_ingreso
        
        años = delta.days // 365
        meses = (delta.days % 365) // 30
        dias = (delta.days % 365) % 30
        
        return {
            'años': años,
            'meses': meses,
            'dias': dias,
            'total_dias': delta.days,
            'texto': f"{años} años, {meses} meses, {dias} días"
        }
    
    def get_dias_vacaciones_disponibles(self):
        """Calcula días de vacaciones disponibles"""
        antiguedad = self.get_antiguedad()
        años_completos = antiguedad['años']
        
        # En Colombia: 15 días hábiles por año trabajado
        dias_ganados = años_completos * 15
        
        # Restar vacaciones tomadas
        dias_tomados = self.vacaciones.filter(aprobada=True).aggregate(
            total=models.Sum(models.F('fecha_fin') - models.F('fecha_inicio'))
        )['total'] or 0
        
        return max(0, dias_ganados - dias_tomados)
    
    def get_contrato_actual(self):
        """Obtiene el contrato activo actual"""
        return self.contratos.filter(activo=True).first()


class Contrato(models.Model):
    """Contratos laborales de empleados"""
    
    TIPO_CONTRATO_CHOICES = [
        ('indefinido', 'Término Indefinido'),
        ('fijo', 'Término Fijo'),
        ('obra_labor', 'Obra o Labor'),
        ('aprendizaje', 'Contrato de Aprendizaje'),
        ('prestacion_servicios', 'Prestación de Servicios'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='contratos')
    numero_contrato = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=30, choices=TIPO_CONTRATO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True, help_text='Dejar vacío para contratos indefinidos')
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    cargo = models.CharField(max_length=100)
    descripcion_funciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    # Archivos
    archivo = models.FileField(upload_to='contratos/', null=True, blank=True)
    
    # Metadata
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contratos_creados')
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.empleado.get_nombre_completo()}"
    
    def esta_vigente(self):
        """Verifica si el contrato está vigente"""
        hoy = date.today()
        if self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin and self.activo
        return hoy >= self.fecha_inicio and self.activo
    
    def dias_para_vencer(self):
        """Calcula días para vencimiento"""
        if not self.fecha_fin:
            return None
        hoy = date.today()
        if hoy > self.fecha_fin:
            return 0
        return (self.fecha_fin - hoy).days
    
    def save(self, *args, **kwargs):
        # Generar número de contrato automáticamente
        if not self.numero_contrato:
            ultimo = Contrato.objects.order_by('-id').first()
            numero = 1 if not ultimo else ultimo.id + 1
            self.numero_contrato = f"{self.empleado.numero_documento}-{numero:02d}"
        
        # Desactivar otros contratos del mismo empleado
        if self.activo:
            Contrato.objects.filter(empleado=self.empleado, activo=True).exclude(id=self.id).update(activo=False)
        
        super().save(*args, **kwargs)


class Certificacion(models.Model):
    """Certificaciones laborales generadas"""
    
    TIPO_CHOICES = [
        ('basica', 'Certificación Laboral Básica'),
        ('detallada', 'Certificación con Detalle Salarial'),
        ('bancaria', 'Certificación para Trámites Bancarios'),
        ('paz_salvo', 'Paz y Salvo Laboral'),
        ('personalizada', 'Certificación Personalizada'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='certificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    destinatario = models.CharField(max_length=200, default='A quien corresponda')
    
    # Información incluida
    incluir_cargo = models.BooleanField(default=True)
    incluir_fecha_ingreso = models.BooleanField(default=True)
    incluir_tipo_contrato = models.BooleanField(default=True)
    incluir_salario = models.BooleanField(default=True)
    incluir_funciones = models.BooleanField(default=False)
    incluir_prestaciones = models.BooleanField(default=False)
    
    contenido_adicional = models.TextField(blank=True)
    
    # Archivo generado
    archivo = models.FileField(upload_to='certificaciones/', null=True, blank=True)
    
    # Metadata
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    generado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Certificación'
        verbose_name_plural = 'Certificaciones'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.empleado.get_nombre_completo()} - {self.fecha_generacion.strftime('%d/%m/%Y')}"


# ============================================================================
# ENTIDADES DE SEGURIDAD SOCIAL
# ============================================================================

class EPS(models.Model):
    """Entidades Promotoras de Salud"""
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    porcentaje_aporte = models.DecimalField(max_digits=5, decimal_places=2, default=12.5)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'EPS'
        verbose_name_plural = 'EPS'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class AFP(models.Model):
    """Administradoras de Fondos de Pensiones"""
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    porcentaje_aporte = models.DecimalField(max_digits=5, decimal_places=2, default=16.0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'AFP'
        verbose_name_plural = 'AFP'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class ARL(models.Model):
    """Administradoras de Riesgos Laborales"""
    
    CLASE_RIESGO_CHOICES = [
        ('I', 'Clase I - Riesgo Mínimo (0.522%)'),
        ('II', 'Clase II - Riesgo Bajo (1.044%)'),
        ('III', 'Clase III - Riesgo Medio (2.436%)'),
        ('IV', 'Clase IV - Riesgo Alto (4.350%)'),
        ('V', 'Clase V - Riesgo Máximo (6.960%)'),
    ]
    
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'ARL'
        verbose_name_plural = 'ARL'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class CajaCompensacion(models.Model):
    """Cajas de Compensación Familiar"""
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    codigo = models.CharField(max_length=20, unique=True)
    porcentaje_aporte = models.DecimalField(max_digits=5, decimal_places=2, default=4.0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Caja de Compensación'
        verbose_name_plural = 'Cajas de Compensación'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ============================================================================
# 3. SELECCIÓN Y TALENTO
# ============================================================================

class PerfilCargo(models.Model):
    """Perfiles de cargo para reclutamiento"""
    
    nombre_cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    nivel_jerarquico = models.CharField(max_length=50, choices=[
        ('operativo', 'Operativo'),
        ('coordinador', 'Coordinador'),
        ('jefe', 'Jefe'),
        ('gerente', 'Gerente'),
        ('director', 'Director'),
    ])
    
    # Descripción
    objetivo_cargo = models.TextField()
    funciones_principales = models.TextField()
    
    # Requisitos
    nivel_educacion = models.CharField(max_length=100)
    experiencia_requerida = models.CharField(max_length=200)
    conocimientos_tecnicos = models.TextField()
    competencias = models.TextField()
    
    # Condiciones
    salario_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salario_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tipo_contrato = models.CharField(max_length=30, choices=Contrato.TIPO_CONTRATO_CHOICES)
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Perfil de Cargo'
        verbose_name_plural = 'Perfiles de Cargo'
        ordering = ['nombre_cargo']
    
    def __str__(self):
        return f"{self.nombre_cargo} - {self.area}"


class Vacante(models.Model):
    """Convocatorias abiertas"""
    
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('en_proceso', 'En Proceso'),
        ('cerrada', 'Cerrada'),
        ('cancelada', 'Cancelada'),
    ]
    
    perfil_cargo = models.ForeignKey(PerfilCargo, on_delete=models.CASCADE, related_name='vacantes')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    numero_vacantes = models.PositiveIntegerField(default=1)
    
    fecha_apertura = models.DateField(default=date.today)
    fecha_cierre = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierta')
    
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vacantes_responsable')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vacante'
        verbose_name_plural = 'Vacantes'
        ordering = ['-fecha_apertura']
    
    def __str__(self):
        return f"{self.titulo} ({self.numero_vacantes} vacantes)"


class Candidato(models.Model):
    """Candidatos para procesos de selección"""
    
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=2, choices=Empleado.TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=20, unique=True)
    
    email = models.EmailField()
    celular = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    
    # Hoja de vida
    archivo_hv = models.FileField(upload_to='candidatos/hojas_vida/')
    nivel_educacion = models.CharField(max_length=100)
    años_experiencia = models.PositiveIntegerField(default=0)
    
    # Calificación general
    calificacion = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Candidato'
        verbose_name_plural = 'Candidatos'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


class ProcesoSeleccion(models.Model):
    """Seguimiento del proceso de selección de cada candidato"""
    
    ETAPA_CHOICES = [
        ('recibida', 'Hoja de Vida Recibida'),
        ('preseleccionado', 'Preseleccionado'),
        ('entrevista', 'Entrevista'),
        ('pruebas', 'Pruebas Técnicas/Psicotécnicas'),
        ('referencias', 'Verificación de Referencias'),
        ('oferta', 'Oferta Laboral'),
        ('contratado', 'Contratado'),
        ('rechazado', 'Rechazado'),
    ]
    
    vacante = models.ForeignKey(Vacante, on_delete=models.CASCADE, related_name='procesos')
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='procesos')
    
    etapa_actual = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='recibida')
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    
    # Evaluaciones
    calificacion_entrevista = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    calificacion_pruebas = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Proceso de Selección'
        verbose_name_plural = 'Procesos de Selección'
        ordering = ['-fecha_aplicacion']
        unique_together = ['vacante', 'candidato']
    
    def __str__(self):
        return f"{self.candidato} - {self.vacante.titulo} ({self.get_etapa_actual_display()})"


# ============================================================================
# 4. CAPACITACIÓN Y DESARROLLO
# ============================================================================

class Capacitacion(models.Model):
    """Plan de capacitaciones"""
    
    TIPO_CHOICES = [
        ('tecnica', 'Técnica Operativa'),
        ('seguridad', 'Seguridad y Salud'),
        ('administrativa', 'Administrativa'),
        ('liderazgo', 'Liderazgo'),
        ('servicio', 'Servicio al Cliente'),
        ('otra', 'Otra'),
    ]
    
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('hibrida', 'Híbrida'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    objetivo = models.TextField()
    
    fecha_programada = models.DateField()
    duracion_horas = models.PositiveIntegerField()
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES)
    
    facilitador = models.CharField(max_length=100)
    lugar = models.CharField(max_length=200, blank=True)
    cupo_maximo = models.PositiveIntegerField(default=30)
    
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Empleados inscritos
    empleados = models.ManyToManyField(Empleado, through='InscripcionCapacitacion', related_name='capacitaciones')
    
    completada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Capacitación'
        verbose_name_plural = 'Capacitaciones'
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_programada}"
    
    def get_inscritos(self):
        return self.empleados.count()


class InscripcionCapacitacion(models.Model):
    """Inscripciones de empleados a capacitaciones"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    asistio = models.BooleanField(default=False)
    calificacion = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    certificado = models.FileField(upload_to='capacitaciones/certificados/', null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Inscripción a Capacitación'
        verbose_name_plural = 'Inscripciones a Capacitaciones'
        unique_together = ['empleado', 'capacitacion']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.capacitacion.nombre}"


# ============================================================================
# 5. SEGURIDAD Y SALUD EN EL TRABAJO (SST)
# ============================================================================

class MatrizRiesgo(models.Model):
    """Matriz de identificación de peligros y riesgos"""
    
    NIVEL_RIESGO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('muy_alto', 'Muy Alto'),
    ]
    
    proceso = models.CharField(max_length=100)
    actividad = models.CharField(max_length=200)
    peligro_identificado = models.TextField()
    tipo_peligro = models.CharField(max_length=100)
    
    efectos_posibles = models.TextField()
    controles_existentes = models.TextField()
    
    nivel_riesgo = models.CharField(max_length=20, choices=NIVEL_RIESGO_CHOICES)
    controles_recomendados = models.TextField()
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Matriz de Riesgo'
        verbose_name_plural = 'Matriz de Riesgos'
        ordering = ['proceso', 'actividad']
    
    def __str__(self):
        return f"{self.proceso} - {self.actividad}"


class ExamenMedico(models.Model):
    """Exámenes médicos ocupacionales"""
    
    TIPO_CHOICES = [
        ('ingreso', 'Examen de Ingreso'),
        ('periodico', 'Examen Periódico'),
        ('retiro', 'Examen de Retiro'),
        ('reintegro', 'Examen de Reintegro'),
    ]
    
    RESULTADO_CHOICES = [
        ('apto', 'Apto'),
        ('apto_condiciones', 'Apto con Condiciones'),
        ('no_apto', 'No Apto'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='examenes_medicos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, blank=True)
    
    ips_realizadora = models.CharField(max_length=200)
    medico_responsable = models.CharField(max_length=100)
    
    observaciones = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    
    archivo = models.FileField(upload_to='sst/examenes_medicos/', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Examen Médico'
        verbose_name_plural = 'Exámenes Médicos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.get_tipo_display()} ({self.fecha})"


class AccidenteTrabajo(models.Model):
    """Investigación de accidentes de trabajo"""
    
    SEVERIDAD_CHOICES = [
        ('leve', 'Leve'),
        ('grave', 'Grave'),
        ('mortal', 'Mortal'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='accidentes')
    fecha_accidente = models.DateTimeField()
    lugar = models.CharField(max_length=200)
    
    descripcion = models.TextField()
    parte_cuerpo_afectada = models.CharField(max_length=100)
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES)
    
    # Investigación
    causas_inmediatas = models.TextField(blank=True)
    causas_basicas = models.TextField(blank=True)
    acciones_correctivas = models.TextField(blank=True)
    
    dias_incapacidad = models.PositiveIntegerField(default=0)
    reportado_arl = models.BooleanField(default=False)
    fecha_reporte_arl = models.DateField(null=True, blank=True)
    
    investigado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_investigacion = models.DateField(null=True, blank=True)
    
    archivo = models.FileField(upload_to='sst/accidentes/', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Accidente de Trabajo'
        verbose_name_plural = 'Accidentes de Trabajo'
        ordering = ['-fecha_accidente']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.fecha_accidente.strftime('%d/%m/%Y')}"


class ElementoProteccion(models.Model):
    """Elementos de Protección Personal (EPP)"""
    
    TIPO_CHOICES = [
        ('cabeza', 'Protección para la Cabeza'),
        ('ojos', 'Protección para los Ojos'),
        ('oidos', 'Protección Auditiva'),
        ('respiratoria', 'Protección Respiratoria'),
        ('manos', 'Protección para Manos'),
        ('pies', 'Protección para Pies'),
        ('cuerpo', 'Protección para el Cuerpo'),
        ('caidas', 'Protección contra Caídas'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=10)
    
    vida_util_dias = models.PositiveIntegerField(help_text='Vida útil en días')
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Elemento de Protección Personal'
        verbose_name_plural = 'Elementos de Protección Personal'
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def requiere_reposicion(self):
        return self.stock_actual <= self.stock_minimo


class EntregaEPP(models.Model):
    """Registro de entrega de EPP a empleados"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='entregas_epp')
    elemento = models.ForeignKey(ElementoProteccion, on_delete=models.CASCADE, related_name='entregas')
    
    cantidad = models.PositiveIntegerField(default=1)
    fecha_entrega = models.DateField(default=date.today)
    fecha_vencimiento = models.DateField()
    
    entregado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    firma_empleado = models.ImageField(upload_to='sst/firmas_epp/', null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Entrega de EPP'
        verbose_name_plural = 'Entregas de EPP'
        ordering = ['-fecha_entrega']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.elemento.nombre} ({self.fecha_entrega})"
    
    def save(self, *args, **kwargs):
        # Calcular fecha de vencimiento automáticamente
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = self.fecha_entrega + timedelta(days=self.elemento.vida_util_dias)
        super().save(*args, **kwargs)


# ============================================================================
# 6. BIENESTAR LABORAL
# ============================================================================

class ActividadBienestar(models.Model):
    """Actividades y eventos de bienestar"""
    
    TIPO_CHOICES = [
        ('deportiva', 'Actividad Deportiva'),
        ('cultural', 'Actividad Cultural'),
        ('recreativa', 'Actividad Recreativa'),
        ('celebracion', 'Celebración'),
        ('integracion', 'Integración'),
        ('salud', 'Salud y Bienestar'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    
    fecha_evento = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(null=True, blank=True)
    
    lugar = models.CharField(max_length=200)
    cupo_maximo = models.PositiveIntegerField(null=True, blank=True)
    
    # Empleados inscritos
    empleados_inscritos = models.ManyToManyField(Empleado, blank=True, related_name='actividades_bienestar')
    
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    completada = models.BooleanField(default=False)
    foto = models.ImageField(upload_to='bienestar/actividades/', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Actividad de Bienestar'
        verbose_name_plural = 'Actividades de Bienestar'
        ordering = ['-fecha_evento']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_evento}"
    
    def get_inscritos(self):
        return self.empleados_inscritos.count()


class EncuestaClimaOrganizacional(models.Model):
    """Encuestas de clima organizacional"""
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    activa = models.BooleanField(default=True)
    anonima = models.BooleanField(default=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Encuesta de Clima'
        verbose_name_plural = 'Encuestas de Clima'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio})"


class RespuestaEncuesta(models.Model):
    """Respuestas a encuestas de clima"""
    
    encuesta = models.ForeignKey(EncuestaClimaOrganizacional, on_delete=models.CASCADE, related_name='respuestas')
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True, blank=True)
    
    calificacion_general = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Dimensiones del clima (1-5)
    liderazgo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comunicacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    trabajo_equipo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    condiciones_trabajo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    reconocimiento = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    desarrollo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    comentarios = models.TextField(blank=True)
    sugerencias = models.TextField(blank=True)
    
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Respuesta a Encuesta'
        verbose_name_plural = 'Respuestas a Encuestas'
        ordering = ['-fecha_respuesta']
    
    def __str__(self):
        return f"Respuesta {self.id} - {self.encuesta.titulo}"


# ============================================================================
# 7. GESTIÓN Y RELACIONES LABORALES
# ============================================================================

class EvaluacionDesempeño(models.Model):
    """Evaluaciones de desempeño de empleados"""
    
    PERIODO_CHOICES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='evaluaciones')
    evaluador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluaciones_realizadas')
    
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES)
    fecha_evaluacion = models.DateField()
    
    # Competencias (1-5)
    calidad_trabajo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    productividad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    conocimiento_tecnico = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    trabajo_equipo = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    iniciativa = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    puntualidad = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, editable=False)
    
    fortalezas = models.TextField()
    areas_mejora = models.TextField()
    plan_desarrollo = models.TextField(blank=True)
    
    observaciones = models.TextField(blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evaluación de Desempeño'
        verbose_name_plural = 'Evaluaciones de Desempeño'
        ordering = ['-fecha_evaluacion']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.fecha_evaluacion}"
    
    def save(self, *args, **kwargs):
        # Calcular promedio automáticamente
        self.calificacion_promedio = (
            self.calidad_trabajo + 
            self.productividad + 
            self.conocimiento_tecnico + 
            self.trabajo_equipo + 
            self.iniciativa + 
            self.puntualidad
        ) / 6.0
        super().save(*args, **kwargs)


class Permiso(models.Model):
    """Permisos y licencias"""
    
    TIPO_CHOICES = [
        ('personal', 'Permiso Personal'),
        ('medico', 'Permiso Médico'),
        ('calamidad', 'Calamidad Doméstica'),
        ('luto', 'Luto'),
        ('estudio', 'Estudio'),
        ('matrimonio', 'Matrimonio'),
        ('paternidad', 'Licencia de Paternidad'),
        ('maternidad', 'Licencia de Maternidad'),
        ('otro', 'Otro'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='permisos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    
    con_goce_sueldo = models.BooleanField(default=True)
    
    aprobado = models.BooleanField(default=False)
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='permisos_aprobados')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    documento_soporte = models.FileField(upload_to='permisos/', null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.get_tipo_display()} ({self.fecha_inicio})"
    
    def get_dias_solicitados(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1


class Vacacion(models.Model):
    """Gestión de vacaciones"""
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='vacaciones')
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_habiles = models.PositiveIntegerField()
    
    aprobada = models.BooleanField(default=False)
    aprobada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vacaciones_aprobadas')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vacación'
        verbose_name_plural = 'Vacaciones'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.fecha_inicio} a {self.fecha_fin}"


class Incapacidad(models.Model):
    """Incapacidades médicas"""
    
    TIPO_CHOICES = [
        ('enfermedad_general', 'Enfermedad General (EPS)'),
        ('accidente_trabajo', 'Accidente de Trabajo (ARL)'),
        ('enfermedad_laboral', 'Enfermedad Laboral (ARL)'),
        ('maternidad', 'Licencia de Maternidad'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='incapacidades')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_incapacidad = models.PositiveIntegerField()
    
    numero_radicado = models.CharField(max_length=50, blank=True)
    entidad_responsable = models.CharField(max_length=100, help_text='EPS o ARL responsable del pago')
    
    diagnostico = models.TextField()
    archivo_incapacidad = models.FileField(upload_to='incapacidades/')
    
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Incapacidad'
        verbose_name_plural = 'Incapacidades'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.get_tipo_display()} ({self.fecha_inicio})"


class Memorando(models.Model):
    """Memorandos y llamados de atención"""
    
    TIPO_CHOICES = [
        ('verbal', 'Llamado de Atención Verbal'),
        ('escrito', 'Llamado de Atención Escrito'),
        ('memorando', 'Memorando'),
        ('suspension', 'Suspensión'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='memorandos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    fecha = models.DateField(default=date.today)
    asunto = models.CharField(max_length=200)
    descripcion_hechos = models.TextField()
    
    archivo = models.FileField(upload_to='memorandos/', null=True, blank=True)
    
    emitido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observaciones = models.TextField(blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Memorando'
        verbose_name_plural = 'Memorandos y Llamados de Atención'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.empleado.get_nombre_completo()} - {self.get_tipo_display()} ({self.fecha})"


class ReglamentoInterno(models.Model):
    """Reglamento interno de trabajo"""
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    version = models.CharField(max_length=20)
    
    archivo = models.FileField(upload_to='reglamentos/')
    fecha_vigencia = models.DateField()
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Reglamento Interno'
        verbose_name_plural = 'Reglamentos Internos'
        ordering = ['-fecha_vigencia']
    
    def __str__(self):
        return f"{self.nombre} v{self.version}"