# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, document_id, password=None, **extra_fields):
        if not document_id:
            raise ValueError('El campo Cédula / RIF es obligatorio')
        
        extra_fields['username'] = document_id
        user = self.model(document_id=document_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, document_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(document_id, password, **extra_fields)


class User(AbstractUser):
    document_id = models.CharField(max_length=20, unique=True, verbose_name="Cédula / RIF")
    phone_number = models.CharField(max_length=20, verbose_name="Número de Teléfono")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección (Opcional)")
    
    is_supplier = models.BooleanField(default=True, verbose_name="Es Proveedor")
    is_supervisor = models.BooleanField(default=False, verbose_name="Es Supervisor")

    objects = CustomUserManager()

    USERNAME_FIELD = 'document_id'
    # Agregamos 'email' a los campos requeridos para el comando createsuperuser
    REQUIRED_FIELDS = ['first_name', 'email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.document_id} - {self.first_name}"