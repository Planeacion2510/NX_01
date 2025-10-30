from django.core.management.base import BaseCommand
from talento_humano.models import EPS, AFP, ARL, CajaCompensacion

class Command(BaseCommand):
    help = "Inicializa las entidades básicas de seguridad social (EPS, AFP, ARL, Caja de Compensación)"

    def handle(self, *args, **kwargs):
        # EPS
        EPS.objects.get_or_create(nombre="Sanitas EPS", nit="800251440", codigo="EPS001")
        EPS.objects.get_or_create(nombre="Sura EPS", nit="800130907", codigo="EPS002")
        EPS.objects.get_or_create(nombre="Nueva EPS", nit="900156264", codigo="EPS003")
        EPS.objects.get_or_create(nombre="Compensar EPS", nit="830053800", codigo="EPS004")

        # AFP
        AFP.objects.get_or_create(nombre="Porvenir", nit="800238476", codigo="AFP001")
        AFP.objects.get_or_create(nombre="Protección", nit="800279457", codigo="AFP002")
        AFP.objects.get_or_create(nombre="Colfondos", nit="800231830", codigo="AFP003")
        AFP.objects.get_or_create(nombre="Skandia", nit="830020188", codigo="AFP004")

        # ARL
        ARL.objects.get_or_create(nombre="ARL Sura", nit="800279457", codigo="ARL001")
        ARL.objects.get_or_create(nombre="ARL Colmena", nit="860514223", codigo="ARL002")
        ARL.objects.get_or_create(nombre="ARL Positiva", nit="860504882", codigo="ARL003")
        ARL.objects.get_or_create(nombre="ARL Bolívar", nit="860002931", codigo="ARL004")

        # Cajas de Compensación
        CajaCompensacion.objects.get_or_create(nombre="Compensar", nit="860007040", codigo="CC001")
        CajaCompensacion.objects.get_or_create(nombre="Colsubsidio", nit="860009008", codigo="CC002")
        CajaCompensacion.objects.get_or_create(nombre="Cafam", nit="860009125", codigo="CC003")
        CajaCompensacion.objects.get_or_create(nombre="Comfama", nit="890905211", codigo="CC004")

        self.stdout.write(self.style.SUCCESS("✅ Entidades de seguridad social creadas o actualizadas correctamente"))
