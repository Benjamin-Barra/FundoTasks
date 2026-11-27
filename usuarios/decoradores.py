from functools import wraps
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Personal, Asistencia


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("usuarios:login")
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "No tienes permiso para acceder a esa sección.")
            return redirect("usuarios:inicio")
        return view_func(request, *args, **kwargs)
    return wrapper


def turno_iniciado_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("usuarios:login")

        # 2. ¿Este usuario es personal activo?
        personal = (
            Personal.objects
            .filter(usuario=request.user)
            .exclude(estado="inactivo")
            .first()
        )

        # 3. Si es admin, no le exigimos turno
        if personal is None:
            return view_func(request, *args, **kwargs)

        # 4. ¿Ya inició turno hoy?
        hoy = timezone.localdate()
        ya_marco = Asistencia.objects.filter(personal=personal, fecha=hoy).exists()

        if ya_marco:
            return view_func(request, *args, **kwargs)   # pasa a la vista normal

        # 5. No ha iniciado turno: le mostramos SOLO la pantalla de iniciar turno
        return render(request, "iniciar_turno.html", {"personal": personal, "hoy": hoy})
    return wrapper