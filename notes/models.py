# Create your models here.
from django.db import models
from django.conf import settings

class Note(models.Model):

    CATEGORY_CHOICES = [
        ('COMPRAS', 'Compras'),
        ('ADMINISTRACION', 'Administración'),
        ('INGENIERIA', 'Ingeniería'),
        ('TOPOGRAFIA', 'Topografía'),
        ('CONTROL_CALIDAD', 'Control de Calidad'),
        ('LOGISTICA', 'Logística'),
        ('RECURSOS_HUMANOS', 'Recursos Humanos'),
        ('SEGURIDAD_HIGIENE', 'Seguridad e Higiene'),
    ]
     
    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notes',
        limit_choices_to={'is_supplier': True}
    )
    title = models.CharField(max_length=200)
    content = models.TextField()

    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        verbose_name="Categoría / Departamento",default='Sin categoría'
    )

    created_at = models.DateTimeField(auto_now_add=True) # Inmutable tras creación
    updated_at = models.DateTimeField(auto_now=True)     # Se actualiza al editar

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title