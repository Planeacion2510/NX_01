<<<<<<< HEAD
# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordentrabajo',
            name='fecha_cierre',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Cierre'),
        ),
        migrations.AddField(
            model_name='ordentrabajo',
            name='cierre_a_tiempo',
            field=models.BooleanField(blank=True, null=True, verbose_name='Cierre a Tiempo'),
        ),
=======
# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordenes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordentrabajo',
            name='fecha_cierre',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Cierre'),
        ),
        migrations.AddField(
            model_name='ordentrabajo',
            name='cierre_a_tiempo',
            field=models.BooleanField(blank=True, null=True, verbose_name='Cierre a Tiempo'),
        ),
>>>>>>> 7f28ea4b99583bb6e745f09358d3439ba5564e95
    ]