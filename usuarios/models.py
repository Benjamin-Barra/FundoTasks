from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone


# Create your models here.

# MODELO PARA QUE UN SUPER USUARIO SEA CREADO CON CARGO ADMIN
class UsuarioManager(UserManager):
    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('cargo', 'admin')
        return super().create_superuser(username, email, password, **extra_fields)

class Usuario(AbstractUser):
    class Cargo(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        SECRETARIO = 'secretario', 'Secretario'
        TRABAJADOR = 'trabajador', 'Trabajador'
        
    email = models.EmailField('correo', max_length=90, unique=True)
    cargo = models.CharField(max_length=30, choices=Cargo.choices, default=Cargo.TRABAJADOR)
    
    @property
    def puede_administrar(self):
        return self.is_superuser or self.cargo in (self.Cargo.ADMIN, self.Cargo.SECRETARIO)
    
    def __str__(self):
        return self.email
    
class Personal(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'activo','Activo'
        INACTIVO = 'inactivo','Inactivo'
        
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=45)
    rut = models.CharField(max_length=12, unique=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    
    def __str__(self):
        return self.nombre
    
class Asistencia(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    estadoAsistencia = models.BooleanField(default=False)
    fecha = models.DateField(default=timezone.localdate)
    
    class Meta:
        unique_together = ('personal', 'fecha')
    
    def __str__(self):
        return f"{self.personal} - {self.fecha} - {'Presente' if self.estadoAsistencia else 'Ausente'}"
    