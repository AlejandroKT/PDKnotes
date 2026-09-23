# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User

# Opciones para el selector
DOCUMENT_TYPE_CHOICES = [
    ('V', 'V'),
    ('J', 'J'),
]

class SupplierRegistrationForm(UserCreationForm):
    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPE_CHOICES,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )
    document_number = forms.CharField(
        label="Número",
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: 28140769',
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone_number', 'address', 'password1', 'password2')
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'w-full h-32 px-3 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Escribe tu direccion.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = False

    def clean_document_number(self):
        """Valida que el número solo contenga dígitos"""
        number = self.cleaned_data.get('document_number')
        if not number.isdigit():
            raise ValidationError("El número solo debe contener dígitos.")
        return number

    def clean(self):
        """Valida que el documento completo (V/J + Número) no exista ya en la base de datos"""
        cleaned_data = super().clean()
        doc_type = cleaned_data.get('document_type')
        doc_number = cleaned_data.get('document_number')

        if doc_type and doc_number:
            full_document_id = f"{doc_type}{doc_number}"
            # Verificamos si ya existe un usuario con esta cédula o RIF
            if User.objects.filter(document_id=full_document_id).exists():
                raise ValidationError(f"Ya existe un usuario registrado con el documento {full_document_id}.")
        
        return cleaned_data

    def save(self, commit=True):
        # Construimos el document_id final y lo asignamos
        user = super().save(commit=False)
        doc_type = self.cleaned_data.get('document_type')
        doc_number = self.cleaned_data.get('document_number')
        
        full_document_id = f"{doc_type}{doc_number}"
        
        user.document_id = full_document_id
        user.username = full_document_id  # Solución al error de duplicate entry ''
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Cédula / RIF",
        widget=forms.TextInput(attrs={
            'autofocus': True, 
            'placeholder': 'Ej: V28140769',
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Cédula / RIF",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'})
    )

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone_number', 'address')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].required = False


    