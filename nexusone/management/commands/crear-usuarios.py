from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = "Crea los usuarios iniciales de NexusOne con sus roles"

    def handle(self, *args, **kwargs):
        # Definimos usuarios con su rol
        usuarios = [
            ("Usuario1", "25102025", True, "Admin"),       # Superusuario
            ("Usuario2", "2510M", False, "Mecanizados"),
            ("Usuario3", "2510E", False, "Ensamble"),
            ("Usuario4", "2510D", False, "Despacho"),
            ("Usuario5", "2510G", False, "Gerencia"),
            ("Usuario6", "2510H", False, "Talento Humano"),
        ]

        for username, password, is_super, rol in usuarios:
            # Crear grupo si no existe
            group, _ = Group.objects.get_or_create(name=rol)

            # Crear usuario si no existe
            if not User.objects.filter(username=username).exists():
                if is_super:
                    user = User.objects.create_superuser(username=username, password=password, email="")
                    self.stdout.write(self.style.SUCCESS(f"Superusuario {username} creado."))
                else:
                    user = User.objects.create_user(username=username, password=password)
                    self.stdout.write(self.style.SUCCESS(f"Usuario {username} creado."))

                # Asignar grupo/rol
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f"→ Asignado al grupo {rol}"))
            else:
                self.stdout.write(self.style.WARNING(f"El usuario {username} ya existe."))
