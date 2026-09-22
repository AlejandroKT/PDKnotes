# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Usaremos document_id (Cédula o RIF) como el identificador único para login
    document_id = models.CharField(max_length=20, unique=True, verbose_name="Cédula / RIF")
    is_supplier = models.BooleanField(default=True, verbose_name="Es Proveedor")
    is_supervisor = models.BooleanField(default=False, verbose_name="Es Supervisor")

    # Configuramos el login para que use document_id en lugar de username
    USERNAME_FIELD = 'document_id'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.document_id} - {self.first_name} {self.last_name}"