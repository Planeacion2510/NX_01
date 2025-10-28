from django.db import models
from django.contrib.auth.models import User

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="empleado", null=True, blank=True)
    documento = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=20, choices=[("activo", "Activo"), ("inactivo", "Inactivo")], default="activo")

    def __str__(self):
        return f"{self.user.get_full_name() if self.user else self.documento}"

class Contrato(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="contratos")
    tipo = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Contrato {self.tipo} - {self.empleado}"

class Vacacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="vacaciones")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    aprobada = models.BooleanField(default=False)

class Permiso(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="permisos")
    fecha = models.DateField()
    motivo = models.CharField(max_length=255)
    aprobado = models.BooleanField(default=False)

class ExamenMedico(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    fecha = models.DateField()
    resultado = models.TextField(blank=True)

class Capacitacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    completado = models.BooleanField(default=False)

class Dotacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    fecha_entrega = models.DateField()
    cantidad = models.PositiveIntegerField()

class Reglamento(models.Model):
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/reglamentos/')
    fecha_subida = models.DateField(auto_now_add=True)

class Memorando(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    asunto = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='documentos/memorandos/')
    fecha_subida = models.DateField(auto_now_add=True)

class HoraExtra(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField()
    horas = models.DecimalField(max_digits=5, decimal_places=2)
    motivo = models.CharField(max_length=255)
    aprobado = models.BooleanField(default=False)

class Ausentismo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=255)
    justificado = models.BooleanField(default=False)

class ExamenPeriodico(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    fecha = models.DateField()
    resultado = models.TextField(blank=True)

class LlamadoAtencion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateField()
    motivo = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True)


