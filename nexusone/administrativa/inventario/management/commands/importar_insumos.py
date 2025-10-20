# Ruta: inventario/management/commands/importar_insumos.py
"""
Comando para importar insumos desde Excel
Uso: python manage.py importar_insumos ruta/al/archivo.xlsx
"""

from django.core.management.base import BaseCommand
from inventario.models import Insumo
import openpyxl
from decimal import Decimal


class Command(BaseCommand):
    help = 'Importa insumos desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='"C:\Users\aux5g\Downloads\NX_01\nexusone\administrativa\inventario\management\commands\Inventario_Procesado.xlsx"')
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Eliminar todos los insumos antes de importar'
        )

    def handle(self, *args, **options):
        archivo = options['archivo']
        limpiar = options['limpiar']

        try:
            # Cargar el archivo Excel
            wb = openpyxl.load_workbook(archivo)
            ws = wb['Inventario_Procesado']  # Nombre de la hoja

            # Limpiar datos si se solicita
            if limpiar:
                conteo = Insumo.objects.count()
                Insumo.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING(f'🗑️  Se eliminaron {conteo} insumos existentes')
                )

            # Contadores
            creados = 0
            actualizados = 0
            errores = 0

            # Iterar sobre las filas (saltar encabezado)
            for row in ws.iter_rows(min_row=2, values_only=True):
                codigo = str(row[0]).strip() if row[0] else None
                nombre = str(row[1]).strip() if row[1] else None
                stock = row[2] if row[2] else 0

                # Validar datos obligatorios
                if not codigo or not nombre:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Fila omitida: código o nombre vacío')
                    )
                    errores += 1
                    continue

                try:
                    # Buscar o crear insumo
                    insumo, created = Insumo.objects.update_or_create(
                        codigo=codigo,
                        defaults={
                            'nombre': nombre,
                            'stock_actual': stock,
                            'descripcion': f'Importado desde Excel',
                            'unidad': 'UND',  # Unidad por defecto
                            'precio_unitario': Decimal('0.00'),
                            'stock_minimo': 0,
                            'stock_maximo': 1000,
                            'iva': Decimal('19.00'),
                            'descuento_proveedor': Decimal('0.00'),
                        }
                    )

                    if created:
                        creados += 1
                        self.stdout.write(f'✅ Creado: {codigo} - {nombre[:50]}')
                    else:
                        actualizados += 1
                        self.stdout.write(f'🔄 Actualizado: {codigo} - {nombre[:50]}')

                except Exception as e:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(f'❌ Error en {codigo}: {str(e)}')
                    )

            # Resumen
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS(f'\n📊 RESUMEN DE IMPORTACIÓN:'))
            self.stdout.write(self.style.SUCCESS(f'   ✅ Creados: {creados}'))
            self.stdout.write(self.style.WARNING(f'   🔄 Actualizados: {actualizados}'))
            if errores > 0:
                self.stdout.write(self.style.ERROR(f'   ❌ Errores: {errores}'))
            self.stdout.write(self.style.SUCCESS(f'\n   Total procesados: {creados + actualizados}'))
            self.stdout.write('='*60 + '\n')

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'❌ Archivo no encontrado: {archivo}')
            )
        except KeyError:
            self.stdout.write(
                self.style.ERROR('❌ No se encontró la hoja "Inventario_Procesado"')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )