from django.forms import ModelForm
from .models import Todo  # модель для объектов туду

class TodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'memo', 'important']  # что будем отображать - список