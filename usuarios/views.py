from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import LoginForm, RegistroForm, ActualizarUsuariosForm , RegistroPersonalForm, ActualizarFuncionarioForm, AutoRegistroForm
from tareas.models import AsignacionTarea

from .models import Personal, Usuario, Asistencia

from core.decoradores import staff_required

# Create your views here.


# SOLO CLASES PARA LA LOGICA DE AUTENTICACIÓN POR DEFECTO QUE TRAE DJANGO

class LoginUsuarioView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

class LogoutUsuarioView(LogoutView):
    pass  

class RegistroView(LoginRequiredMixin, UserPassesTestMixin,CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('usuarios:inicio')
    
    def test_func(self):
        u = self.request.user
        return u.is_superuser or u.cargo in ('admin', 'secretario')

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'No tienes permiso para registrar usuarios.')
            return redirect('usuarios:inicio') 
        return super().handle_no_permission()

class AutoRegistroView(CreateView):
    form_class = AutoRegistroForm
    template_name = 'auth/auto_register.html'
    success_url = reverse_lazy('usuarios:login')

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.is_authenticated:
            return redirect('usuarios:inicio')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(
            self.request,
            "Cuenta creada. Podrás entrar cuando el administrador te apruebe."
        )
        return super().form_valid(form)
    
class EditarUsuarioView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Usuario
    form_class = ActualizarUsuariosForm
    template_name = 'auth/register.html'
    
    success_url = reverse_lazy('usuarios:list_usuarios')
    
    def test_func(self):
        editor = self.request.user
        objetivo = self.get_object()

        puede_gestionar = editor.is_superuser or editor.cargo in ('admin', 'secretario')
        
        # un secretario no toca cuentas de admin
        if objetivo.cargo == 'admin' and not (editor.is_superuser or editor.cargo == 'admin'):
            return False
        return puede_gestionar

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'No tienes permiso para editar este usuario.')
            return redirect('usuarios:inicio')
        return super().handle_no_permission()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar usuario'
        context['boton'] = 'Guardar cambios'
        return context


# VAMOS A PONER LAS FUNCIONES AQUÍ


@login_required
def inicio_view(request):
    hoy = timezone.localdate()
    personal = Personal.objects.filter(usuario=request.user).first()

    tareas_hoy = AsignacionTarea.objects.filter(personal=personal, tarea__fechaProgramada=hoy).select_related('tarea') if personal else AsignacionTarea.objects.none()

    ya_marco = bool(personal) and Asistencia.objects.filter(personal=personal, fecha=hoy, estadoAsistencia=True).exists()

    return render(request, 'inicio.html', {'personal': personal,'tareas_hoy': tareas_hoy,'ya_marco': ya_marco,'hoy': hoy,})

@staff_required
def listado_usuarios(request):
    usuarios = Usuario.objects.all()
    
    return render(request, "listado_usuarios.html", {"usuarios": usuarios})

@staff_required
def registrar_personal(request):
    if request.method == "POST":
        form = RegistroPersonalForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                personal = form.save()
                usuario = personal.usuario
                # Al aprobar a alguien, su cuenta pasa a estar activa
                if not usuario.is_active:
                    usuario.is_active = True
                    usuario.save(update_fields=["is_active"])
            messages.success(request, "Personal asignado con éxito.")
            return redirect("usuarios:list_personal")
        messages.error(request, "¡Ocurrió un error al asignar personal!")
    else:
        form = RegistroPersonalForm()

    return render(request, "crear_editar_personal.html", {"form": form,"titulo": "Registrar personal",})

@login_required
def perfil_personal(request, id):
    personal = get_object_or_404(Personal.objects.select_related("usuario"), id=id)

    u = request.user
    es_gestor = u.puede_administrar
    es_el_mismo = personal.usuario_id == u.pk

    if not (es_gestor or es_el_mismo):
        messages.error(request, "No tienes permiso para ver este perfil.")
        return redirect("usuarios:inicio")

    asignaciones = AsignacionTarea.objects.filter(personal=personal).select_related("tarea")

    pendientes = asignaciones.filter(
        estadoAsignacion=AsignacionTarea.EstadoTarea.PENDIENTE
    ).order_by("tarea__fechaProgramada")

    completadas = asignaciones.filter(
        estadoAsignacion=AsignacionTarea.EstadoTarea.COMPLETADA
    ).order_by("-tarea__fechaProgramada")[:10]

    asistencias = Asistencia.objects.filter(personal=personal).order_by("-fecha")[:10]

    return render(request, "perfil_personal.html", { "personal": personal, "pendientes": pendientes, "completadas": completadas, "asistencias": asistencias, "es_gestor": es_gestor,})

@staff_required
def listado_personal(request):
    personal = Personal.objects.select_related("usuario")
    
    return render(request, "listado_personal.html", {"personal": personal})

@staff_required
def editar_personal(request, id):
    personal = get_object_or_404(Personal.objects.select_related("usuario"), id=id)

    if request.method == "POST":
        form = ActualizarFuncionarioForm(request.POST, instance=personal)
        if form.is_valid():
            with transaction.atomic():
                personal = form.save()
                usuario = personal.usuario
                # La cuenta sigue al estado: activo => puede entrar, inactivo => no.
                # Nadie se bloquea a sí mismo desde esta pantalla.
                if usuario.pk != request.user.pk:
                    activo = personal.estado == "activo"
                    if usuario.is_active != activo:
                        usuario.is_active = activo
                        usuario.save(update_fields=["is_active"])
            messages.success(request, "Los datos del personal se actualizaron correctamente.")
            return redirect("usuarios:list_personal")
        messages.error(request, "¡Ocurrió un error al actualizar el personal!")
    else:
        form = ActualizarFuncionarioForm(instance=personal)

    return render(request, "crear_editar_personal.html", {
        "form": form,
        "titulo": "Editar personal",
        "editando": True,
    })
    
@staff_required
@require_POST
def baja_personal(request, id):
    personal = get_object_or_404(Personal.objects.select_related("usuario"), id=id)

    if personal.usuario_id == request.user.pk:
        messages.error(request, "No puedes darte de baja a ti mismo.")
    elif personal.estado == "inactivo":
        messages.warning(request, f"{personal.nombre} ya estaba dado de baja.")
    else:
        with transaction.atomic():
            personal.estado = "inactivo"
            personal.save(update_fields=["estado"])
            personal.usuario.is_active = False
            personal.usuario.save(update_fields=["is_active"])
        messages.success(request, f"{personal.nombre} fue dado de baja correctamente.")

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