from django.contrib.auth import get_user_model
from django.core.management import call_command

def run():
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        print("⚙️  Creando superusuario admin automáticamente...")
        User.objects.create_superuser("admin", "admin@example.com", "admin1234")
        call_command("loaddata", "backup.json", verbosity=1)
