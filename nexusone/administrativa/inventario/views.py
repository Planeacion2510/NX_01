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
