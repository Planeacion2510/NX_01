from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    Empleado, Contrato, Vacacion, Permiso, 
    ExamenMedico, Capacitacion, Dotacion,
    Reglamento, Memorando
)
from .forms import (
    EmpleadoForm, ContratoForm, VacacionForm, PermisoForm,
    ReglamentoForm, MemorandoForm
)

@login_required
def menu_talento_humano(request):
    return render(request, "talento_humano/menu_talento.html")

# ---------------- EMPLEADOS ----------------
@login_required
def lista_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, "talento_humano/empleados/lista_empleados.html", {"empleados": empleados})

@login_required
def nuevo_empleado(request):
    form = EmpleadoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Empleado registrado correctamente.")
        return redirect("talento_humano:lista_empleados")
    return render(request, "talento_humano/empleados/form_empleado.html", {"form": form})

# ---------------- CONTRATOS ----------------
@login_required
def lista_contratos(request):
    contratos = Contrato.objects.select_related("empleado")
    return render(request, "talento_humano/contratos/lista_contratos.html", {"contratos": contratos})

@login_required
def nuevo_contrato(request):
    form = ContratoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Contrato creado exitosamente.")
        return redirect("talento_humano:lista_contratos")
    return render(request, "talento_humano/contratos/form_contrato.html", {"form": form})

# ---------------- VACACIONES ----------------
@login_required
def lista_vacaciones(request):
    vacaciones = Vacacion.objects.select_related("empleado")
    return render(request, "talento_humano/vacaciones/lista_vacaciones.html", {"vacaciones": vacaciones})

@login_required
def nueva_vacacion(request):
    form = VacacionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Vacaciones registradas.")
        return redirect("talento_humano:lista_vacaciones")
    return render(request, "talento_humano/vacaciones/form_vacacion.html", {"form": form})

# ---------------- PERMISOS ----------------
@login_required
def lista_permisos(request):
    permisos = Permiso.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleado/permisos.html", {"permisos": permisos})

@login_required
def nuevo_permiso(request):
    form = PermisoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Permiso registrado.")
        return redirect("talento_humano:lista_permisos")
    return render(request, "talento_humano/gestion_empleado/form_permiso.html", {"form": form})

# ---------------- REGLAMENTO ----------------
@login_required
def lista_reglamentos(request):
    reglamentos = Reglamento.objects.all()
    return render(request, "talento_humano/gestion_empleado/reglamento.html", {"reglamentos": reglamentos})

@login_required
def nuevo_reglamento(request):
    form = ReglamentoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Reglamento subido correctamente.")
        return redirect("talento_humano:lista_reglamentos")
    return render(request, "talento_humano/gestion_empleado/form_reglamento.html", {"form": form})

# ---------------- MEMORANDOS ----------------
@login_required
def lista_memorandos(request):
    memorandos = Memorando.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleado/memorandos.html", {"memorandos": memorandos})

@login_required
def nuevo_memorando(request):
    form = MemorandoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Memorando registrado correctamente.")
        return redirect("talento_humano:lista_memorandos")
    return render(request, "talento_humano/gestion_empleado/form_memorando.html", {"form": form})
