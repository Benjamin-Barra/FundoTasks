from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import AsignacionTarea
from .forms import CrearTareaForm, AsignarTareaForm
from django.db import transaction
from core.decoradores import staff_required
from usuarios.models import Personal

# Create your views here.


@login_required
def lista_tareas_asignadas(request):
    asignaciones = AsignacionTarea.objects.filter(personal__usuario=request.user).select_related('tarea')
    
    return render(request, 'tareas.html', asignaciones)


@login_required
@staff_required
def crear_tareaView(request):
    if request.method == 'POST':
        form = CrearTareaForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea creada con éxito")
            return redirect("usuarios:list_usuarios")
        messages.error(request, "¡Ocurrió un error al crear la tarea!")
    else:
        form = CrearTareaForm() 
        
    return render(request, "crear_editar_tarea.html", {"form" : form})

@login_required
def ver_mis_tareasView(request):
    mis_asignaciones = (AsignacionTarea.objects.filter(personal__usuario=request.user).select_related('tarea'))

    pendientes = mis_asignaciones.filter(estadoAsignacion=AsignacionTarea.EstadoTarea.PENDIENTE).order_by('tarea__fechaProgramada')

    completadas = mis_asignaciones.filter(estadoAsignacion=AsignacionTarea.EstadoTarea.COMPLETADA).order_by('-tarea__fechaProgramada')

    return render(request, "tareas.html", {"pendientes": pendientes,"completadas": completadas,})

@login_required
def asignar_tareaView(request):
    if request.method == "POST":
        form = AsignarTareaForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request,"Tarea asignada correctamente")
            return redirect("tareas:ini_tareas")
        messages.error(request,"Error al asignar tarea.")
    else:
        form = AsignarTareaForm()
        
    return render(request, "asignar_tarea.html", {"form":form})

@login_required
def completar_tarea(request, id):
    
    tarea = get_object_or_404(AsignacionTarea, id=id)
    
    with transaction.atomic():
        tarea.estadoAsignacion = "completada"
        tarea.save(update_fields=["estadoAsignacion"])
    messages.success(request, f"Tarea '{tarea.tarea.nombreTarea}' fue completada.")
        
    return redirect("tareas:ini_tareas")