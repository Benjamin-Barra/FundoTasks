from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path('', views.inicio_view, name="inicio"),
    path('login', views.LoginUsuarioView.as_view(), name="login"),
    path('register', views.RegistroView.as_view(), name="register"),
    path('logout', views.LogoutUsuarioView.as_view(), name="logout"),
    path('marcar_asistencia', views.marcar_asistencia, name="marcar_asistencia"),
    path('administracion/registrar_personal', views.registrar_personal, name="regis_personal"),
    path('administracion/lista_personal', views.listado_personal, name="list_personal"),
    path('administracion/editar_personal/<int:id>', views.editar_personal, name="edit_personal"),
    path('administracion/baja_personal/<int:id>', views.baja_personal, name="baja_personal")
]