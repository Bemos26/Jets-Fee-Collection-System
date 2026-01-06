from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    """
    Custom Login Form to apply our specific styling widgets.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input', 
        'placeholder': 'Username or Admission No.'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 
        'placeholder': 'Password'
    }))
