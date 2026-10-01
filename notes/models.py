from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

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
        verbose_name="Categoría / Departamento",
        default='COMPRAS'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return self.title


class NoteAttachment(models.Model):
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
    
    note = models.ForeignKey(
        Note, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(
        upload_to='notes/attachments/%Y/%m/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=ALLOWED_EXTENSIONS,
                message='Solo se permiten archivos: JPG, PNG, PDF, Word y Excel'
            )
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note.title} - {self.file.name}"
    
    @property
    def file_type(self):
        """Retorna el tipo de archivo para mostrar ícono apropiado"""
        ext = self.file.name.split('.')[-1].lower()
        
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif ext == 'pdf':
            return 'pdf'
        elif ext in ['doc', 'docx']:
            return 'word'
        elif ext in ['xls', 'xlsx']:
            return 'excel'
        return 'other'
    
    @property
    def filename(self):
        """Retorna solo el nombre del archivo sin la ruta completa"""
        return self.file.name.split('/')[-1]