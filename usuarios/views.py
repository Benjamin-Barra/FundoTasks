from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def inicio_view(request):
    return render(request,'inicio.html')


def registro_usuarios(request):
    return render(request, 'register.html')

def iniciar_usuarios(request):
    return render(request,'login.html')