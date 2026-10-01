from django import forms
from .models import Note

from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    # Campo para múltiples archivos - SIN widget con multiple
    attachments = forms.FileField(
        required=False,
        label="Archivos adjuntos (Opcional)",
        help_text="Puedes seleccionar múltiples archivos (Ctrl + clic). Máximo 10 archivos de 2 MB c/u."
    )

    class Meta:
        model = Note
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
            'content': forms.Textarea(attrs={
                'rows': 5, 
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white',
            }),
        }

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        
        if files:
            if len(files) > 10:
                raise forms.ValidationError('No se pueden adjuntar más de 10 archivos.')
            
            for f in files:
                if f.size > 2 * 1024 * 1024:
                    raise forms.ValidationError(f'El archivo "{f.name}" no puede superar los 2 MB.')
        
        return files