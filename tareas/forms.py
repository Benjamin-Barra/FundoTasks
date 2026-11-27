from django import forms
from .models import Tarea, AsignacionTarea


from usuarios.forms import ESTILO
from usuarios.models import Personal


class CrearTareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ('nombreTarea', 'descripcion', 'fechaProgramada')
        labels = {
            'nombreTarea': 'Nombre de la tarea',
            'descripcion': 'Descripción',
            'fechaProgramada': 'Fecha programada',
        }
        widgets = {
            'nombreTarea': forms.TextInput(attrs={'placeholder': 'Ingrese el nombre de la tarea'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ingrese la descripción de la tarea'}),
            'fechaProgramada': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = ESTILO
        
        
class AsignarTareaForm(forms.ModelForm):
    class Meta:
        model = AsignacionTarea
        fields = ('personal','tarea')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = ESTILO

        # Solo personal activo
        self.fields['personal'].queryset = Personal.objects.filter(
            estado=Personal.Estado.ACTIVO
        ).order_by('nombre')
        self.fields['personal'].empty_label = 'Seleccione una persona'

        self.fields['tarea'].queryset = Tarea.objects.order_by('-fechaProgramada')
        self.fields['tarea'].empty_label = 'Seleccione una tarea'