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
def lista_empleados(request):
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
        e.contrato_pdf = ultimo_contrato.archivo.url if ultimo_contrato and ultimo_contrato.archivo else None

    return render(request, "talento_humano/lista_empleados.html", {"empleados": empleados})

@login_required
def nuevo_empleado(request):
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
            return redirect("talento_humano:lista_empleados")
    else:
        form = EmpleadoForm()
    return render(request, "talento_humano/form_empleado.html", {"form": form, "titulo": "Nuevo empleado"})

@login_required
def editar_empleado(request, pk):
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
            return redirect("talento_humano:lista_empleados")
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, "talento_humano/form_empleado.html", {"form": form, "titulo": "Editar empleado"})

@login_required
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.delete()
    messages.success(request, "Empleado eliminado correctamente.")
    return redirect("talento_humano:lista_empleados")

# ---------------- CONTRATOS ----------------
@login_required
def lista_contratos(request):
    contratos = Contrato.objects.all().select_related('empleado')
    return render(request, "talento_humano/lista_contratos.html", {"contratos": contratos})

@login_required
def nuevo_contrato(request):
    if request.method == "POST":
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Contrato creado correctamente.")
            return redirect("talento_humano:lista_contratos")
    else:
        form = ContratoForm()
    return render(request, "talento_humano/form_contrato.html", {"form": form, "titulo": "Nuevo contrato"})

# ---------------- VACACIONES ----------------
@login_required
def lista_vacaciones(request):
    vacaciones = Vacacion.objects.all().select_related('empleado')
    return render(request, "talento_humano/lista_vacaciones.html", {"vacaciones": vacaciones})

@login_required
def nueva_vacacion(request):
    if request.method == "POST":
        form = VacacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vacación creada correctamente.")
            return redirect("talento_humano:lista_vacaciones")
    else:
        form = VacacionForm()
    return render(request, "talento_humano/form_vacacion.html", {"form": form, "titulo": "Nueva vacación"})

# ---------------- PERMISOS ----------------
@login_required
def lista_permisos(request):
    permisos = Permiso.objects.all().select_related('empleado')
    return render(request, "talento_humano/lista_permisos.html", {"permisos": permisos})

@login_required
def nuevo_permiso(request):
    if request.method == "POST":
        form = PermisoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Permiso creado correctamente.")
            return redirect("talento_humano:lista_permisos")
    else:
        form = PermisoForm()
    return render(request, "talento_humano/form_permiso.html", {"form": form, "titulo": "Nuevo permiso"})

# ---------------- REGLAMENTOS ----------------
@login_required
def lista_reglamentos(request):
    reglamentos = Reglamento.objects.all()
    return render(request, "talento_humano/lista_reglamentos.html", {"reglamentos": reglamentos})

@login_required
def nuevo_reglamento(request):
    if request.method == "POST":
        form = ReglamentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Reglamento creado correctamente.")
            return redirect("talento_humano:lista_reglamentos")
    else:
        form = ReglamentoForm()
    return render(request, "talento_humano/form_reglamento.html", {"form": form, "titulo": "Nuevo reglamento"})

# ---------------- MEMORANDOS ----------------
@login_required
def lista_memorandos(request):
    memorandos = Memorando.objects.all().select_related('empleado')
    return render(request, "talento_humano/lista_memorandos.html", {"memorandos": memorandos})

@login_required
def nuevo_memorando(request):
    if request.method == "POST":
        form = MemorandoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Memorando creado correctamente.")
            return redirect("talento_humano:lista_memorandos")
    else:
        form = MemorandoForm()
    return render(request, "talento_humano/form_memorando.html", {"form": form, "titulo": "Nuevo memorando"})