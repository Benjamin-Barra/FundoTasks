from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AsignacionTarea

# Create your views here.


@login_required
def lista_tareas(request):
    asignaciones = AsignacionTarea.objects.filter(personal__usuario=request.user).select_related('tarea')
    
    return render(request, 'tareas.html', asignaciones)

@login_required
def crear_tarea(request):
    return