# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SupplierRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        # Agregamos email, phone_number y address
        fields = ('document_id', 'first_name', 'email', 'phone_number', 'address', 'password1', 'password2')
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 2, 
                'cols': 40,
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el campo dirección sea opcional en el formulario
        self.fields['address'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.document_id
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Cédula / RIF",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )