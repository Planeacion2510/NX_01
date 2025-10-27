# nexusone/talento_humano/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Empleado, Contrato, Vacacion, Permiso
from .forms import EmpleadoForm, ContratoForm, VacacionForm, PermisoForm

@login_required(login_url="/login/")
def menu_talento_humano(request):
    """Menú principal del módulo Talento Humano"""
    return render(request, "talento_humano/menu_talento.html")

@login_required(login_url="/login/")
def lista_empleados(request):
    empleados = Empleado.objects.select_related("user").all()
    return render(request, "talento_humano/empleados/lista_empleados.html", {"empleados": empleados})

@login_required(login_url="/login/")
def detalle_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    contratos = empleado.contratos.all()
    return render(request, "talento_humano/empleados/detalle_empleado.html", {"empleado": empleado, "contratos": contratos})

@login_required(login_url="/login/")
def nuevo_contrato(request):
    if request.method == "POST":
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Contrato creado correctamente")
            return redirect("talento_humano:menu_talento_humano")
    else:
        form = ContratoForm()
    return render(request, "talento_humano/contratos/nuevo_contrato.html", {"form": form})

@login_required(login_url="/login/")
def lista_vacaciones(request):
    vacaciones = Vacacion.objects.select_related("empleado").all()
    return render(request, "talento_humano/documentos/vacaciones.html", {"vacaciones": vacaciones})

@login_required(login_url="/login/")
def lista_permisos(request):
    permisos = Permiso.objects.select_related("empleado").all()
    return render(request, "talento_humano/documentos/permisos.html", {"permisos": permisos})
