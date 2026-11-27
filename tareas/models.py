from django.db import models
from django.utils import timezone
from usuarios.models import Personal

# Create your models here.

class Tarea(models.Model):
    
    nombreTarea = models.CharField(max_length=100)
    descripcion = models.TextField()
    fechaProgramada = models.DateField()
    
    def __str__(self):
        return self.nombreTarea
    
class AsignacionTarea(models.Model):
    class EstadoTarea(models.TextChoices):
        COMPLETADA = 'completada','Completada'
        PENDIENTE = 'pendiente', 'Pendiente'
    
    class Meta:
        unique_together = ('personal', 'tarea')
        
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    fechaAsignacion = models.DateField(default=timezone.localdate)
    estadoAsignacion = models.CharField(max_length=20, choices=EstadoTarea.choices , default=EstadoTarea.PENDIENTE)
    
    def __str__(self):
        return f"{self.tarea} -> {self.personal} ({self.get_estadoAsignacion_display()})"