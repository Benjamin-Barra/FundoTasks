from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario, Personal, Asistencia

ESTILO = (
    "block w-full rounded-md border-slate-300 shadow-sm "
    "focus:border-emerald-500 focus:ring-emerald-500 sm:text-sm p-2 border"
)


#LOGIN Y CREACIÓN DE USUARIOS

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['username'].widget.attrs.update({
            'class': ESTILO,
            'placeholder': 'tu usuario',
        })
        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs.update({
            'class': ESTILO,
            'placeholder': '••••••••',
        })

    def confirm_login_allowed(self, user):
        if not user.is_active:
            if hasattr(user, 'personal'):
                msg = 'Tu cuenta fue desactivada. Habla con el administrador.'
            else:
                msg = 'Tu cuenta aún está pendiente de aprobación. Avisa al administrador.'
            raise forms.ValidationError(msg, code='inactive')

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'cargo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = ESTILO
            campo.help_text = ''

class AutoRegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email') 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = ESTILO
            campo.help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.cargo = Usuario.Cargo.TRABAJADOR 
        user.is_active = False               
        if commit:
            user.save()
        return user
            
class ActualizarUsuariosForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'cargo')

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = ESTILO

        es_admin = editor and (editor.is_superuser or editor.cargo == 'admin')

        # Un secretario no puede asignar "admin"
        if editor and not es_admin:
            self.fields['cargo'].choices = [
                c for c in Usuario.Cargo.choices if c[0] != Usuario.Cargo.ADMIN
            ]

        # Nadie se cambia el cargo a sí mismo (evita quedarse sin admin)
        if editor and self.instance.pk == editor.pk:
            self.fields['cargo'].disabled = True
            
            

# FORMULARIOS DE PERSONAL
            
class RegistroPersonalForm(forms.ModelForm):
    INPUT_CLASSES = (
        "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm text-gray-900 "
        "placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
    )

    class Meta:
        model = Personal
        fields = ("usuario", "nombre", "rut", "estado")
        widgets = {
            "usuario": forms.Select(),
            "nombre": forms.TextInput(attrs={"placeholder": "Ingrese el nombre completo"}),
            "rut": forms.TextInput(attrs={"placeholder": "Ingrese el RUT"}),
            "estado": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = self.INPUT_CLASSES

        # Solo usuarios que aún no están asignados como personal
        asignados = Personal.objects.values_list("usuario_id", flat=True)
        queryset = self.fields["usuario"].queryset.exclude(pk__in=asignados)

        # Si estamos editando, el usuario actual debe seguir apareciendo
        if self.instance.pk:
            queryset = self.fields["usuario"].queryset.filter(
                pk__in=list(queryset.values_list("pk", flat=True)) + [self.instance.usuario_id]
            )

        self.fields["usuario"].queryset = queryset
        self.fields["usuario"].empty_label = "Seleccione un usuario"
            
    def clean_rut(self):
        rut = self.cleaned_data["rut"].replace(".", "").replace("-", "").upper()
        cuerpo, dv = rut[:-1], rut[-1]
        if not cuerpo.isdigit():
            raise forms.ValidationError("RUT inválido.")

        suma, factor = 0, 2
        for d in reversed(cuerpo):
            suma += int(d) * factor
            factor = 2 if factor == 7 else factor + 1
        resto = 11 - (suma % 11)
        esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)

        if dv != esperado:
            raise forms.ValidationError("RUT inválido.")
        return f"{cuerpo}-{dv}"
    
class ActualizarFuncionarioForm(RegistroPersonalForm):
    class Meta(RegistroPersonalForm.Meta):
        fields = ("usuario", "nombre", "rut", "estado")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El usuario asignado no se cambia al editar
        self.fields["usuario"].disabled = True