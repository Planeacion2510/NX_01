from django.shortcuts import render, get_object_or_404, redirect
from .models import Insumo, Maquinaria, Herramienta, MovimientoKardex
from .forms import InsumoForm, MaquinariaForm, HerramientaForm, MovimientoKardexForm
from django.utils import timezone


def index_inventario(request):
    return render(request, "administrativa/inventario/index.html")
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from .models import Insumo
from .forms import InsumoForm

# ==============================
# 📌 INSUMOS
# ==============================
def lista_insumo(request):
    insumos = Insumo.objects.all()

    # Calculamos el total del inventario usando la propiedad precio_total
    total_inventario = sum(insumo.precio_total for insumo in insumos)

    return render(
        request,
        "administrativa/inventario/insumos/lista_insumo.html",
        {"proveedores": insumos, "total_inventario": total_inventario}
    )

def nuevo_insumo(request):
    if request.method == "POST":
        form = InsumoForm(request.POST)
        if form.is_valid():
            insumo = form.save(commit=False)

            # Guardamos solo los valores editables
            insumo.iva = Decimal(request.POST.get("iva", 0))
            insumo.descuento_proveedor = Decimal(request.POST.get("descuento_proveedor", 0))
            insumo.save()

            return redirect("inventario:lista_insumo")
    else:
        form = InsumoForm()
    return render(request, "administrativa/inventario/insumos/form_insumo.html", {"form": form})

def editar_insumo(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    if request.method == "POST":
        form = InsumoForm(request.POST, instance=insumo)
        if form.is_valid():
            insumo = form.save(commit=False)

            # Actualizamos solo campos editables
            insumo.iva = Decimal(request.POST.get("iva", 0))
            insumo.descuento_proveedor = Decimal(request.POST.get("descuento_proveedor", 0))
            insumo.save()

            return redirect("inventario:lista_insumo")
    else:
        form = InsumoForm(instance=insumo)
    return render(request, "administrativa/inventario/insumos/form_insumo.html", {"form": form})

def eliminar_insumo(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    insumo.delete()
    return redirect("inventario:lista_insumo")
# ==============================
# 📌 MAQUINARIA
# ==============================
def lista_maquinaria(request):
    maquinaria = Maquinaria.objects.all()
    return render(request, "administrativa/inventario/maquinaria/listar_maquinaria.html", {"maquinaria": maquinaria})

def nueva_maquinaria(request):
    if request.method == "POST":
        form = MaquinariaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:lista_maquinaria")
    else:
        form = MaquinariaForm()
    return render(request, "administrativa/inventario/maquinaria/nueva_maquinaria.html", {"form": form})

def editar_maquinaria(request, pk):
    maquina = get_object_or_404(Maquinaria, pk=pk)
    if request.method == "POST":
        form = MaquinariaForm(request.POST, instance=maquina)
        if form.is_valid():
            form.save()
            return redirect("inventario:lista_maquinaria")
    else:
        form = MaquinariaForm(instance=maquina)
    return render(request, "administrativa/inventario/maquinaria/nueva_maquinaria.html", {"form": form})

def eliminar_maquinaria(request, pk):
    maquina = get_object_or_404(Maquinaria, pk=pk)
    if request.method == "POST":
        maquina.delete()
        return redirect("inventario:lista_maquinaria")
    return render(request, "administrativa/inventario/maquinaria/nueva_maquinaria.html", {"form": None, "delete": True})

# ==============================
# 📌 HERRAMIENTAS
# ==============================
def lista_herramientas(request):
    herramientas = Herramienta.objects.all()
    return render(request, "administrativa/inventario/herramientas/listar_herramientas.html", {"herramientas": herramientas})

def nueva_herramienta(request):
    if request.method == "POST":
        form = HerramientaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventario:lista_herramientas")
    else:
        form = HerramientaForm()
    return render(request, "administrativa/inventario/herramientas/nueva_herramienta.html", {"form": form})

def editar_herramienta(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == "POST":
        form = HerramientaForm(request.POST, instance=herramienta)
        if form.is_valid():
            form.save()
            return redirect("inventario:lista_herramientas")
    else:
        form = HerramientaForm(instance=herramienta)
    return render(request, "administrativa/inventario/herramientas/nueva_herramienta.html", {"form": form})

def eliminar_herramienta(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == "POST":
        herramienta.delete()
        return redirect("inventario:lista_herramientas")
    return render(request, "administrativa/inventario/herramientas/nueva_herramienta.html", {"form": None, "delete": True})

# ==============================
# 📌 KARDEX
# ==============================
def listar_kardex(request):
    """Listar todos los movimientos del Kardex."""
    movimientos = MovimientoKardex.objects.all().order_by('-fecha')
    return render(request, "administrativa/inventario/kardex/listar_kardex.html", {"movimientos": movimientos})

def registrar_movimiento_kardex(request):
    """Registrar un nuevo movimiento en el Kardex."""
    if request.method == "POST":
        form = MovimientoKardexForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            # Si no se envía fecha, usar la fecha actual
            if not movimiento.fecha:
                movimiento.fecha = timezone.now()
            movimiento.save()
            return redirect("inventario:listar_kardex")
    else:
        # Inicializamos el formulario con fecha actual
        form = MovimientoKardexForm(initial={"fecha": timezone.now()})
    return render(request, "administrativa/inventario/kardex/nuevo_movimiento.html", {"form": form})

def editar_movimiento(request, pk):
    """Editar un movimiento existente del Kardex."""
    movimiento = get_object_or_404(MovimientoKardex, pk=pk)
    if request.method == "POST":
        form = MovimientoKardexForm(request.POST, instance=movimiento)
        if form.is_valid():
            movimiento = form.save(commit=False)
            # Si no hay fecha, asignar la actual
            if not movimiento.fecha:
                movimiento.fecha = timezone.now()
            movimiento.save()
            return redirect("inventario:listar_kardex")
    else:
        form = MovimientoKardexForm(instance=movimiento)
    return render(request, "administrativa/inventario/kardex/nuevo_movimiento.html", {"form": form})

def eliminar_movimiento(request, pk):
    movimiento = get_object_or_404(MovimientoKardex, pk=pk)
    movimiento.delete()
    return redirect("inventario:listar_kardex")
    
    # Confirmación de eliminación
    return render(request, "administrativa/inventario/kardex/confirmar_eliminar.html", {"movimiento": movimiento})

# ==============================
# 📥 IMPORTAR DESDE EXCEL
# Agregar esta función AL FINAL de tu archivo inventario/views.py
# ==============================

def importar_excel(request):
    """
    Vista para importar insumos desde Excel
    Solo lee la hoja "Inventario_Procesado" (ignora hoja 2)
    Columnas esperadas: Código, Nombre, Stock
    """
    
    if request.method == 'POST':
        archivo = request.FILES.get('archivo_excel')
        limpiar = request.POST.get('limpiar') == 'on'
        
        # Validaciones
        if not archivo:
            messages.error(request, '❌ Debes seleccionar un archivo')
            return redirect('administrativa:inventario:importar_excel')
        
        if not archivo.name.endswith(('.xlsx', '.xls')):
            messages.error(request, '❌ El archivo debe ser .xlsx o .xls')
            return redirect('administrativa:inventario:importar_excel')
        
        try:
            import openpyxl
            
            # Leer el archivo Excel
            wb = openpyxl.load_workbook(archivo)
            
            # Buscar hoja "Inventario_Procesado" o usar la primera
            if 'Inventario_Procesado' in wb.sheetnames:
                ws = wb['Inventario_Procesado']
            else:
                ws = wb.active
                messages.warning(request, f'⚠️ Usando hoja: {ws.title}')
            
            # Limpiar base de datos si se solicita
            if limpiar:
                count = Insumo.objects.count()
                Insumo.objects.all().delete()
                messages.warning(request, f'🗑️ Se eliminaron {count} insumos existentes')
            
            # Contadores
            creados = 0
            actualizados = 0
            errores = []
            
            # Procesar cada fila (empezar desde fila 2, omitir encabezado)
            for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                
                # Validar que la fila tenga datos
                if not row or len(row) < 3:
                    continue
                
                # Leer solo las 3 primeras columnas
                codigo = str(row[0]).strip() if row[0] else None
                nombre = str(row[1]).strip() if row[1] else None
                
                # Convertir stock a entero
                try:
                    stock_inicial = int(row[2]) if row[2] else 0
                except (ValueError, TypeError):
                    stock_inicial = 0
                
                # Validar datos obligatorios
                if not codigo or not nombre:
                    errores.append(f'Fila {idx}: código o nombre vacío')
                    continue
                
                try:
                    # Crear o actualizar insumo
                    insumo, created = Insumo.objects.update_or_create(
                        codigo=codigo,
                        defaults={
                            'nombre': nombre,
                            'descripcion': 'Importado desde Excel',
                            'unidad': 'UND',
                            'precio_unitario': Decimal('0.00'),
                            'stock_minimo': 0,
                            'stock_maximo': 1000,
                            'iva': Decimal('19.00'),
                            'descuento_proveedor': Decimal('0.00'),
                        }
                    )
                    
                    # Si es nuevo Y tiene stock, crear movimiento de entrada
                    if created and stock_inicial > 0:
                        MovimientoKardex.objects.create(
                            insumo=insumo,
                            tipo='entrada',
                            cantidad=stock_inicial,
                            observacion='Stock inicial importado desde Excel',
                            fecha=timezone.now()
                        )
                        creados += 1
                    else:
                        actualizados += 1
                
                except Exception as e:
                    errores.append(f'Fila {idx} ({codigo}): {str(e)}')
            
            # Mostrar resultados
            if creados > 0:
                messages.success(request, f'✅ {creados} insumos creados con stock inicial')
            
            if actualizados > 0:
                messages.info(request, f'🔄 {actualizados} insumos ya existían (no se modificó su stock)')
            
            if errores:
                # Mostrar máximo 5 errores
                for error in errores[:5]:
                    messages.warning(request, f'⚠️ {error}')
                if len(errores) > 5:
                    messages.warning(request, f'⚠️ ... y {len(errores) - 5} errores más')
            
            # Redirigir si hubo éxito
            if creados > 0 or actualizados > 0:
                messages.success(request, '🎉 ¡Importación completada!')
                return redirect('administrativa:inventario:lista_insumo')
        
        except ImportError:
            messages.error(request, '❌ Instala openpyxl: pip install openpyxl')
        except Exception as e:
            messages.error(request, f'❌ Error al procesar: {str(e)}')
        
        return redirect('administrativa:inventario:importar_excel')
    
    # GET: Mostrar formulario de importación
    return render(request, 'administrativa/inventario/insumos/importar_excel.html')

# ==============================
# 📤 EXPORTAR A EXCEL
# Agregar esta función en tu inventario/views.py
# ==============================

def exportar_excel(request):
    """
    Exporta el inventario actual a Excel en tiempo real
    Solo una hoja: Inventario (Código, Nombre, Stock Actual)
    """
    from django.http import HttpResponse
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from datetime import datetime
    
    # Obtener todos los insumos
    insumos = Insumo.objects.all().order_by('codigo')
    
    # Crear libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    
    # ========================================
    # ESTILOS
    # ========================================
    
    # Estilo del encabezado (amarillo)
    header_fill = PatternFill(start_color="FACC15", end_color="FACC15", fill_type="solid")
    header_font = Font(bold=True, size=12, color="000000")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Bordes
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # ========================================
    # ENCABEZADOS
    # ========================================
    headers = ['Código', 'Nombre', 'Stock']
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # ========================================
    # DATOS
    # ========================================
    for row_num, insumo in enumerate(insumos, 2):
        # Código
        cell = ws.cell(row=row_num, column=1)
        cell.value = insumo.codigo
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")
        
        # Nombre
        cell = ws.cell(row=row_num, column=2)
        cell.value = insumo.nombre
        cell.border = thin_border
        
        # Stock Actual
        cell = ws.cell(row=row_num, column=3)
        cell.value = insumo.stock_actual
        cell.border = thin_border
        cell.alignment = Alignment(horizontal="center")
    
    # ========================================
    # AJUSTAR ANCHO DE COLUMNAS
    # ========================================
    ws.column_dimensions['A'].width = 15  # Código
    ws.column_dimensions['B'].width = 60  # Nombre
    ws.column_dimensions['C'].width = 12  # Stock
    
    # ========================================
    # PREPARAR RESPUESTA HTTP
    # ========================================
    
    # Nombre del archivo con fecha actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f"Inventario_{fecha_actual}.xlsx"
    
    # Configurar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    # Guardar el archivo en la respuesta
    wb.save(response)
    
    return response
