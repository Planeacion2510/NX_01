from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from .models import Constructora, Proyecto
from .forms import ConstructoraForm, ProyectoForm
import os


# ===================================
# 📋 LISTAR PROYECTOS Y CONSTRUCTORAS
# ===================================
@login_required(login_url='/login/')
def listar_proyectos(request):
    """
    Vista principal del módulo de proyectos.
    Muestra todas las constructoras y sus proyectos.
    """
    constructoras = Constructora.objects.all().prefetch_related('proyectos')
    
    # Filtros opcionales
    filtro_estado = request.GET.get('estado', '')
    buscar = request.GET.get('buscar', '')
    
    proyectos = Proyecto.objects.all()
    
    if filtro_estado:
        proyectos = proyectos.filter(estado=filtro_estado)
    
    if buscar:
        proyectos = proyectos.filter(
            nombre__icontains=buscar
        ) | proyectos.filter(
            codigo__icontains=buscar
        ) | proyectos.filter(
            constructora__razon_social__icontains=buscar
        )
    
    context = {
        'constructoras': constructoras,
        'proyectos': proyectos,
        'filtro_estado': filtro_estado,
        'buscar': buscar,
        'ESTADO_CHOICES': Proyecto.ESTADO_CHOICES,
    }
    return render(request, 'administrativa/proyectos/listar_proyectos.html', context)


# ===================================
# 🏢 CONSTRUCTORA - CREAR
# ===================================
@login_required(login_url='/login/')
def crear_constructora(request):
    """Crear una nueva constructora"""
    if request.method == 'POST':
        form = ConstructoraForm(request.POST)
        if form.is_valid():
            constructora = form.save()
            messages.success(request, f'✅ Constructora "{constructora.razon_social}" creada exitosamente.')
            return redirect('administrativa:proyectos:listar_proyectos')
    else:
        form = ConstructoraForm()
    
    context = {
        'form': form,
        'title': 'Registrar Constructora',
        'action': 'crear'
    }
    return render(request, 'administrativa/proyectos/form_constructora.html', context)


# ===================================
# 🏢 CONSTRUCTORA - EDITAR
# ===================================
@login_required(login_url='/login/')
def editar_constructora(request, pk):
    """Editar una constructora existente"""
    constructora = get_object_or_404(Constructora, pk=pk)
    
    if request.method == 'POST':
        form = ConstructoraForm(request.POST, instance=constructora)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Constructora "{constructora.razon_social}" actualizada exitosamente.')
            return redirect('administrativa:proyectos:listar_proyectos')
    else:
        form = ConstructoraForm(instance=constructora)
    
    context = {
        'form': form,
        'constructora': constructora,
        'title': 'Editar Constructora',
        'action': 'editar'
    }
    return render(request, 'administrativa/proyectos/form_constructora.html', context)


# ===================================
# 🏢 CONSTRUCTORA - ELIMINAR
# ===================================
@login_required(login_url='/login/')
def eliminar_constructora(request, pk):
    """Eliminar una constructora (solo si no tiene proyectos)"""
    constructora = get_object_or_404(Constructora, pk=pk)
    
    # Verificar si tiene proyectos
    if constructora.proyectos.exists():
        messages.error(
            request, 
            f'❌ No se puede eliminar la constructora "{constructora.razon_social}" porque tiene {constructora.total_proyectos} proyecto(s) asociado(s).'
        )
    else:
        razon_social = constructora.razon_social
        constructora.delete()
        messages.success(request, f'✅ Constructora "{razon_social}" eliminada exitosamente.')
    
    return redirect('administrativa:proyectos:listar_proyectos')


# ===================================
# 🏢 CONSTRUCTORA - VER DETALLE
# ===================================
@login_required(login_url='/login/')
def detalle_constructora(request, pk):
    """Ver todos los proyectos de una constructora"""
    constructora = get_object_or_404(Constructora, pk=pk)
    proyectos = constructora.proyectos.all()
    
    context = {
        'constructora': constructora,
        'proyectos': proyectos,
    }
    return render(request, 'administrativa/proyectos/detalle_constructora.html', context)


# ===================================
# 🏗️ PROYECTO - CREAR
# ===================================
@login_required(login_url='/login/')
def crear_proyecto(request):
    """Crear un nuevo proyecto"""
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            proyecto = form.save()
            messages.success(request, f'✅ Proyecto "{proyecto.nombre}" creado exitosamente.')
            return redirect('administrativa:proyectos:listar_proyectos')
    else:
        # Preseleccionar constructora si viene en la URL
        constructora_id = request.GET.get('constructora')
        initial = {}
        if constructora_id:
            initial['constructora'] = constructora_id
        form = ProyectoForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Registrar Proyecto',
        'action': 'crear'
    }
    return render(request, 'administrativa/proyectos/form_proyecto.html', context)


# ===================================
# 🏗️ PROYECTO - EDITAR
# ===================================
@login_required(login_url='/login/')
def editar_proyecto(request, pk):
    """Editar un proyecto existente"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Proyecto "{proyecto.nombre}" actualizado exitosamente.')
            return redirect('administrativa:proyectos:listar_proyectos')
    else:
        form = ProyectoForm(instance=proyecto)
    
    context = {
        'form': form,
        'proyecto': proyecto,
        'title': 'Editar Proyecto',
        'action': 'editar'
    }
    return render(request, 'administrativa/proyectos/form_proyecto.html', context)


# ===================================
# 🏗️ PROYECTO - ELIMINAR
# ===================================
@login_required(login_url='/login/')
def eliminar_proyecto(request, pk):
    """Eliminar un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    nombre = proyecto.nombre
    
    # Eliminar el archivo de contrato si existe
    if proyecto.contrato:
        if os.path.exists(proyecto.contrato.path):
            os.remove(proyecto.contrato.path)
    
    proyecto.delete()
    messages.success(request, f'✅ Proyecto "{nombre}" eliminado exitosamente.')
    
    return redirect('administrativa:proyectos:listar_proyectos')


# ===================================
# 📄 DESCARGAR CONTRATO
# ===================================
@login_required(login_url='/login/')
def descargar_contrato(request, pk):
    """Descargar el contrato de un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if not proyecto.contrato:
        raise Http404("Este proyecto no tiene contrato")
    
    if not os.path.exists(proyecto.contrato.path):
        raise Http404("El archivo de contrato no existe")
    
    return FileResponse(
        open(proyecto.contrato.path, 'rb'),
        as_attachment=True,
        filename=f"Contrato_{proyecto.codigo}.pdf"
    )


# ===================================
# 🗑️ ELIMINAR CONTRATO
# ===================================
@login_required(login_url='/login/')
def eliminar_contrato(request, pk):
    """Eliminar el contrato de un proyecto"""
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if proyecto.contrato:
        if os.path.exists(proyecto.contrato.path):
            os.remove(proyecto.contrato.path)
        proyecto.contrato = None
        proyecto.save()
        messages.success(request, f'✅ Contrato del proyecto "{proyecto.nombre}" eliminado exitosamente.')
    else:
        messages.warning(request, f'⚠️ El proyecto "{proyecto.nombre}" no tiene contrato.')
    
    return redirect('administrativa:proyectos:editar_proyecto', pk=pk)