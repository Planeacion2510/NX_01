from django.shortcuts import render

def menu_administrativa(request):
    return render(request, "administrativa/menu.html")
