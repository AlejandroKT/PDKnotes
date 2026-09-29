# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Note
from django.core.paginator import Paginator 
from accounts.models import User
from .forms import NoteForm
from django.db.models import Q
from datetime import datetime

#Modelo CustomUser para traer a los proveedores
from accounts.models import User


# Decoradores para verificar roles
def supplier_required(view_func):
    return user_passes_test(lambda u: u.is_supplier, login_url='login')(view_func)

def supervisor_required(view_func):
    return user_passes_test(lambda u: u.is_supervisor, login_url='login')(view_func)

# --- SUPPLIER VIEWS ---
@login_required
@supplier_required
def supplier_dashboard(request):
    notes = Note.objects.filter(supplier=request.user)
    return render(request, 'notes/supplier_dashboard.html', {'notes': notes})

@login_required
@supplier_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.supplier = request.user
            note.save()
            messages.success(request, 'Nota creada con exito.')
            return redirect('supplier_dashboard')
    else:
        form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Create'})

@login_required
@supplier_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, supplier=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
@supplier_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, supplier=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota actualizada correctamente.')
            return redirect('supplier_dashboard')
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Edit', 'note': note})

@login_required
@supplier_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, supplier=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully.')
        return redirect('supplier_dashboard')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

# --- SUPERVISOR VIEWS ---

@login_required
@supervisor_required
def supervisor_dashboard(request):
    suppliers = User.objects.filter(is_supplier=True)
    return render(request, 'notes/supervisor_dashboard.html', {'suppliers': suppliers})

@login_required
@supervisor_required
def supervisor_supplier_notes(request, supplier_id):
    supplier = get_object_or_404(User, pk=supplier_id, is_supplier=True)
    notes = Note.objects.filter(supplier=supplier)
    return render(request, 'notes/supervisor_supplier_notes.html', {'supplier': supplier, 'notes': notes})

@login_required
@supervisor_required
def supervisor_note_detail(request, pk):
    # El supervisor puede ver cualquier nota, sin filtrar por supplier=request.user
    note = get_object_or_404(Note, pk=pk)
    return render(request, 'notes/supervisor_note_detail.html', {'note': note})

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required
def supervisor_table(request):
    # 1. Obtenemos todas las notas ordenadas
    notes = Note.objects.select_related('supplier').order_by('-created_at')
    
    # 2. Procesar filtros
    supplier_filter = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # VALIDACIÓN EN BACKEND: Verificar que fecha desde no sea mayor que fecha hasta
    if date_from and date_to and date_from > date_to:
        messages.error(request, 'La fecha "Desde" no puede ser superior a la fecha "Hasta"')
        # No aplicamos los filtros de fecha si son inválidos
        date_from = None
        date_to = None
    
    # Aplicar filtro por proveedor
    if supplier_filter:
        notes = notes.filter(supplier_id=supplier_filter)
    
    # Aplicar filtro por fecha desde (solo si pasó la validación)
    if date_from:
        notes = notes.filter(created_at__date__gte=date_from)
    
    # Aplicar filtro por fecha hasta (solo si pasó la validación)
    if date_to:
        notes = notes.filter(created_at__date__lte=date_to)
    
    # 3. Obtener proveedores únicos para el filtro
    suppliers = User.objects.filter(is_supplier=True).order_by('first_name')
    
    # 4. Configuramos el paginador
    paginator = Paginator(notes, 15)
    page_number = request.GET.get('page')
    
    # 5. Obtenemos el objeto de página actual
    page_obj = paginator.get_page(page_number)
    
    # Si hubo error, no mostramos las fechas inválidas en el formulario
    if date_from is None and date_to is None and request.GET.get('date_from') and request.GET.get('date_to'):
        current_date_from = ''
        current_date_to = ''
    else:
        current_date_from = date_from or ''
        current_date_to = date_to or ''
    
    return render(request, 'notes/supervisor_table.html', {
        'page_obj': page_obj,
        'total_notes': notes.count(),
        'suppliers': suppliers,
        'current_filters': {
            'supplier': supplier_filter or '',
            'date_from': current_date_from,
            'date_to': current_date_to,
        }
    })