# nexusone/talento_humano/models.py
from django.db import models
from django.contrib.auth.models import User

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="empleado")
    documento = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    tipo_contrato = models.CharField(max_length=50, choices=[
        ("indefinido", "Indefinido"),
        ("fijo", "Fijo"),
        ("obra", "Obra o labor"),
        ("aprendizaje", "Aprendizaje"),
    ])
    estado = models.CharField(max_length=20, default="activo", choices=[
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("retirado", "Retirado"),
    ])

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.cargo})"


class Contrato(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="contratos")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=12, decimal_places=2)
    archivo = models.FileField(upload_to="contratos/", blank=True, null=True)

    def __str__(self):
        return f"Contrato de {self.empleado.user.get_full_name()}"


class DocumentoEmpresa(models.Model):
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="documentos_empresa/")
    fecha_publicacion = models.DateField(auto_now_add=True)
    tipo = models.CharField(max_length=50, choices=[
        ("reglamento", "Reglamento de trabajo"),
        ("politica_sst", "Política SST"),
        ("manual_funciones", "Manual de funciones"),
    ])

    def __str__(self):
        return self.titulo


class Vacacion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"Vacaciones {self.empleado} ({self.fecha_inicio} - {self.fecha_fin})"


class Permiso(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"Permiso de {self.empleado.user.get_full_name()}"


class LlamadoAtencion(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    tipo = models.CharField(max_length=30, choices=[
        ("leve", "Leve"),
        ("grave", "Grave"),
    ])

    def __str__(self):
        return f"Llamado a {self.empleado.user.get_full_name()} ({self.tipo})"
