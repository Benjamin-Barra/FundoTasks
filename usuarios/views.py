from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm, RegistroPersonalForm, ActualizarFuncionarioForm
from tareas.models import AsignacionTarea

from .models import Personal, Usuario, Asistencia

from .decoradores import staff_required, turno_iniciado_required

# Create your views here.


# SOLO CLASES PARA LA LOGICA DE AUTENTICACIÓN POR DEFECTO QUE TRAE DJANGO

class LoginUsuarioView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutUsuarioView(LogoutView):
    pass  


class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('usuarios:login')


# VAMOS A PONER LAS FUNCIONES AQUÍ


@login_required
@turno_iniciado_required
def inicio_view(request):
    hoy = timezone.localdate()
    tareas_hoy = AsignacionTarea.objects.filter(personal__usuario=request.user, tarea__fechaProgramada=hoy).select_related('tarea')
    
    
    return render(request, 'inicio.html', {'tareas_hoy': tareas_hoy, 'hoy' : hoy})

@staff_required
def registrar_personal(request):
    if request.method == "POST":
        form = RegistroPersonalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal asignado con éxito.")
            return redirect("usuarios:inicio")
        messages.error(request, "¡Ocurrió un error al asignar personal!")
    else:
        form = RegistroPersonalForm()

    return render(request, "crear_editar_personal.html", {"form": form, "titulo": "Registrar personal",})

@staff_required
def listado_personal(request):
    personal = Personal.objects.select_related("usuario")
    
    return render(request, "listado_personal.html", {"personal": personal})

@staff_required
def editar_personal(request, id):
    personal = get_object_or_404(Personal, id=id)

    if request.method == "POST":
        form = ActualizarFuncionarioForm(request.POST, instance=personal)
        if form.is_valid():
            form.save()
            messages.success(request, "Los datos del personal se actualizaron correctamente.")
            return redirect("usuarios:list_personal")
        messages.error(request, "¡Ocurrió un error al actualizar el personal!")
    else:
        form = ActualizarFuncionarioForm(instance=personal)

    return render(request, "crear_editar_personal.html", {
        "form": form,
        "editando": True,
    })
    
@staff_required
def baja_personal(request, id):
    
    personal_buscado = get_object_or_404(Personal, id=id)
    if personal_buscado.estado == "inactivo":
        messages.warning(request, f"{personal_buscado.nombre} ya estaba dado de baja.")
    else:
        personal_buscado.estado = "inactivo"
        personal_buscado.save(update_fields=["estado"])
        messages.success(request, f"{personal_buscado.nombre} fue dado de baja correctamente.")

    return redirect("usuarios:list_personal")

@login_required
@require_POST
def marcar_asistencia(request):
    personal = (
        Personal.objects.filter(usuario=request.user).exclude(estado="inactivo").first()
    )

    if personal is None:
        messages.error(request, "Tu usuario no está registrado como personal activo.")
        return redirect("usuarios:inicio")

    asistencia, creada = Asistencia.objects.get_or_create(
        personal=personal,
        fecha=timezone.localdate(),
        defaults={"estadoAsistencia": True},
    )

    if creada:
        messages.success(request, "¡Turno iniciado! Que tengas un buen día.")
    else:
        messages.info(request, "Ya habías iniciado tu turno hoy.")

    return redirect("usuarios:inicio")