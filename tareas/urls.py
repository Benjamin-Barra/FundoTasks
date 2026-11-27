from django.urls import path
from . import views

app_name = "tareas"

urlpatterns = [
    path('', views.inicio_view, name="inicio"),
    path('login/', views.LoginUsuarioView.as_view(), name="login"),
    path('register/', views.RegistroView.as_view(), name="register"),
    path('logout/', views.LogoutUsuarioView.as_view(), name="logout"),
]