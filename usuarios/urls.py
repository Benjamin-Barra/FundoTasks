from django.urls import path

from . import views

app_name = "usuarios" 

urlpatterns = [
    path('', views.inicio_view, name="inicio"),
    path('login/', views.iniciar_usuarios, name="login"),
    path('register/', views.registro_usuarios, name="register")
]
