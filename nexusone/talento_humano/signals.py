from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Empleado, Contrato, Permiso, Vacacion, AccidenteTrabajo

# ============================================================================
# SEÑALES PARA EMPLEADOS
# ============================================================================

@receiver(post_save, sender=Empleado)
def crear_usuario_empleado(sender, instance, created, **kwargs):
    """Crear usuario automáticamente al crear empleado"""
    if created and not instance.user:
        # Generar username único
        username = f"{instance.primer_nombre.lower()}.{instance.primer_apellido.lower()}"
        
        # Verificar si existe
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=instance.email_corporativo,
            first_name=instance.primer_nombre,
            last_name=f"{instance.primer_apellido} {instance.segundo_apellido}".strip(),
        )
        
        instance.user = user
        instance.save()


@receiver(pre_save, sender=Empleado)
def generar_email_corporativo(sender, instance, **kwargs):
    """Generar email corporativo si no existe"""
    if not instance.email_corporativo and instance.primer_nombre and instance.primer_apellido:
        instance.email_corporativo = f"{instance.primer_nombre.lower()}.{instance.primer_apellido.lower()}@dinnova.com.co"


# ============================================================================
# SEÑALES PARA CONTRATOS
# ============================================================================

@receiver(post_save, sender=Contrato)
def actualizar_salario_empleado(sender, instance, created, **kwargs):
    """Actualizar salario del empleado cuando se crea/actualiza contrato"""
    if instance.activo:
        empleado = instance.empleado
        empleado.salario_basico = instance.salario
        empleado.save()


# ============================================================================
# SEÑALES PARA PERMISOS Y VACACIONES
# ============================================================================

@receiver(post_save, sender=Permiso)
def notificar_aprobacion_permiso(sender, instance, created, **kwargs):
    """Enviar notificación cuando se aprueba un permiso"""
    if not created and instance.aprobado:
        # Aquí iría la lógica de envío de email
        pass


@receiver(post_save, sender=Vacacion)
def notificar_aprobacion_vacacion(sender, instance, created, **kwargs):
    """Enviar notificación cuando se aprueban vacaciones"""
    if not created and instance.aprobada:
        # Aquí iría la lógica de envío de email
        pass


# ============================================================================
# SEÑALES PARA SST
# ============================================================================

@receiver(post_save, sender=AccidenteTrabajo)
def notificar_accidente_trabajo(sender, instance, created, **kwargs):
    """Notificar inmediatamente cuando ocurre un accidente"""
    if created:
        # Enviar notificación urgente al equipo SST
        # Aquí iría la lógica de notificación
        pass