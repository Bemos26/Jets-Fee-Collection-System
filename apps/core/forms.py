from django import forms
from .models import StudentClass

class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Form 5'}),
        }
