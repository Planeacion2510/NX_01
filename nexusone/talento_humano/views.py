from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import (
    Empleado, Contrato, Vacacion, Permiso,
    ExamenMedico, Capacitacion, Dotacion,
    Reglamento, Memorando, HoraExtra,
    Ausentismo, ExamenPeriodico, LlamadoAtencion
)
from .forms import (
    EmpleadoForm, ContratoForm, VacacionForm, PermisoForm,
    ExamenMedicoForm, CapacitacionForm, DotacionForm,
    ReglamentoForm, MemorandoForm, HoraExtraForm,
    AusentismoForm, ExamenPeriodicoForm, LlamadoAtencionForm
)

# ---------------- MENU ----------------
@login_required
def menu_talento_humano(request):
    return render(request, "talento_humano/menu_talento.html")

# ---------------- EMPLEADOS ----------------
@login_required
def empleados_list(request):
    empleados = Empleado.objects.all()

    for e in empleados:
        if e.fecha_ingreso:
            hoy = timezone.now().date()
            delta = hoy - e.fecha_ingreso
            años = delta.days // 365
            meses = (delta.days % 365) // 30
            e.antiguedad = f"{años} años, {meses} meses"
        else:
            e.antiguedad = "N/A"

        ultimo_contrato = e.contratos.order_by("-fecha_inicio").first()
        e.contrato_pdf = ultimo_contrato.archivo.url if ultimo_contrato and hasattr(ultimo_contrato, "archivo") and ultimo_contrato.archivo else None

    return render(request, "empleados/empleados_list.html", {"empleados": empleados})

@login_required
def empleado_create(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            empleado = form.save()
            contrato_pdf = form.cleaned_data.get("contrato_pdf")
            if contrato_pdf:
                Contrato.objects.create(
                    empleado=empleado,
                    tipo="Contrato inicial",
                    fecha_inicio=empleado.fecha_ingreso,
                    salario=0,
                    activo=True,
                    archivo=contrato_pdf
                )
            messages.success(request, "Empleado creado correctamente.")
            return redirect("empleados_list")
    else:
        form = EmpleadoForm()
    return render(request, "empleados/empleado_form.html", {"form": form, "titulo": "Nuevo empleado"})

@login_required
def empleado_update(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == "POST":
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            empleado = form.save()
            contrato_pdf = form.cleaned_data.get("contrato_pdf")
            if contrato_pdf:
                Contrato.objects.create(
                    empleado=empleado,
                    tipo="Actualización de contrato",
                    fecha_inicio=empleado.fecha_ingreso,
                    salario=0,
                    activo=True,
                    archivo=contrato_pdf
                )
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect("empleados_list")
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, "empleados/empleado_form.html", {"form": form, "titulo": "Editar empleado"})

@login_required
def empleado_delete(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.delete()
    messages.success(request, "Empleado eliminado correctamente.")
    return redirect("empleados_list")
