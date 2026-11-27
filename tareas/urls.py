from django.urls import path
from . import views

app_name = "tareas"

urlpatterns = [
    path('mis_tareas', views.ver_mis_tareasView, name="ini_tareas"),
    path('crear_tarea', views.crear_tareaView, name="cre_tarea"),
    path('asignar_tarea', views.asignar_tareaView, name="asign_tarea"),
    path('completar_tarea/<int:id>', views.completar_tarea, name="completar_tarea")
]