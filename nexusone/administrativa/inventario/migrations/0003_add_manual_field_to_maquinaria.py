from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0002_remove_insumo_descripcion_insumo_proveedor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maquinaria',
            name='manual',
            field=models.FileField(
                upload_to='manuales/',
                blank=True,
                null=True,
                verbose_name='Manual',
                help_text='Archivo PDF del manual de la maquinaria'
            ),
        ),
    ]
