from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
    return render(request, "talento_humano/gestion_empleados/permisos.html", {"permisos": permisos})

@login_required
def nuevo_permiso(request):
    form = PermisoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Permiso registrado.")
        return redirect("talento_humano:lista_permisos")
    return render(request, "talento_humano/gestion_empleados/form_permiso.html", {"form": form})

# ---------------- REGLAMENTOS ----------------
@login_required
def lista_reglamentos(request):
    reglamentos = Reglamento.objects.all()
    return render(request, "talento_humano/gestion_empleados/reglamento.html", {"reglamentos": reglamentos})

@login_required
def nuevo_reglamento(request):
    form = ReglamentoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Reglamento subido correctamente.")
        return redirect("talento_humano:lista_reglamentos")
    return render(request, "talento_humano/gestion_empleados/form_reglamento.html", {"form": form})

# ---------------- MEMORANDOS ----------------
@login_required
def lista_memorandos(request):
    memorandos = Memorando.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleados/memorandos.html", {"memorandos": memorandos})

@login_required
def nuevo_memorando(request):
    form = MemorandoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Memorando registrado correctamente.")
        return redirect("talento_humano:lista_memorandos")
    return render(request, "talento_humano/gestion_empleados/form_memorando.html", {"form": form})

# ---------------- HORAS EXTRAS ----------------
@login_required
def lista_horas_extras(request):
    horas_extras = HoraExtra.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleados/horas_extras.html", {"horas_extras": horas_extras})

@login_required
def nueva_hora_extra(request):
    form = HoraExtraForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hora extra registrada correctamente.")
        return redirect("talento_humano:lista_horas_extras")
    return render(request, "talento_humano/gestion_empleados/form_hora_extra.html", {"form": form})

@login_required
def editar_hora_extra(request, pk):
    hora_extra = get_object_or_404(HoraExtra, pk=pk)
    form = HoraExtraForm(request.POST or None, instance=hora_extra)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hora extra actualizada correctamente.")
        return redirect("talento_humano:lista_horas_extras")
    return render(request, "talento_humano/gestion_empleados/form_hora_extra.html", {"form": form})

@login_required
def eliminar_hora_extra(request, pk):
    hora_extra = get_object_or_404(HoraExtra, pk=pk)
    hora_extra.delete()
    messages.success(request, "Hora extra eliminada correctamente.")
    return redirect("talento_humano:lista_horas_extras")

# ---------------- AUSENTISMOS ----------------
@login_required
def lista_ausentismos(request):
    ausentismos = Ausentismo.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleados/ausentismos.html", {"ausentismos": ausentismos})

@login_required
def nuevo_ausentismo(request):
    form = AusentismoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ausentismo registrado correctamente.")
        return redirect("talento_humano:lista_ausentismos")
    return render(request, "talento_humano/gestion_empleados/form_ausentismo.html", {"form": form})

@login_required
def editar_ausentismo(request, pk):
    ausentismo = get_object_or_404(Ausentismo, pk=pk)
    form = AusentismoForm(request.POST or None, instance=ausentismo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ausentismo actualizado correctamente.")
        return redirect("talento_humano:lista_ausentismos")
    return render(request, "talento_humano/gestion_empleados/form_ausentismo.html", {"form": form})

@login_required
def eliminar_ausentismo(request, pk):
    ausentismo = get_object_or_404(Ausentismo, pk=pk)
    ausentismo.delete()
    messages.success(request, "Ausentismo eliminado correctamente.")
    return redirect("talento_humano:lista_ausentismos")

# ---------------- EXÁMENES PERIÓDICOS ----------------
@login_required
def lista_examenes_periodicos(request):
    examenes = ExamenPeriodico.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleados/examenes_periodicos.html", {"examenes": examenes})

@login_required
def nuevo_examen_periodico(request):
    form = ExamenPeriodicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Examen periódico registrado correctamente.")
        return redirect("talento_humano:lista_examenes_periodicos")
    return render(request, "talento_humano/gestion_empleados/form_examen_periodico.html", {"form": form})

@login_required
def editar_examen_periodico(request, pk):
    examen = get_object_or_404(ExamenPeriodico, pk=pk)
    form = ExamenPeriodicoForm(request.POST or None, instance=examen)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Examen periódico actualizado correctamente.")
        return redirect("talento_humano:lista_examenes_periodicos")
    return render(request, "talento_humano/gestion_empleados/form_examen_periodico.html", {"form": form})

@login_required
def eliminar_examen_periodico(request, pk):
    examen = get_object_or_404(ExamenPeriodico, pk=pk)
    examen.delete()
    messages.success(request, "Examen periódico eliminado correctamente.")
    return redirect("talento_humano:lista_examenes_periodicos")

# ---------------- LLAMADOS DE ATENCIÓN ----------------
@login_required
def lista_llamados(request):
    llamados = LlamadoAtencion.objects.select_related("empleado")
    return render(request, "talento_humano/gestion_empleados/llamados.html", {"llamados": llamados})

@login_required
def nuevo_llamado(request):
    form = LlamadoAtencionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Llamado de atención registrado correctamente.")
        return redirect("talento_humano:lista_llamados")
    return render(request, "talento_humano/gestion_empleados/form_llamado_atencion.html", {"form": form})
