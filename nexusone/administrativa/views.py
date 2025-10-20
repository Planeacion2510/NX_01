from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def menu_administrativa(request):
    """
    Menú principal de la Dirección Administrativa.
    Muestra las tarjetas de acceso a los submódulos:
    - Órdenes de Trabajo
    - Inventario
    - Compras
    """
    return render(request, "administrativa/menu_administrativa.html")