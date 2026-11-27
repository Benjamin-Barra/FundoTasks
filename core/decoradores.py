from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


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

