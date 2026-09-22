# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Note
from accounts.models import User
from .forms import NoteForm

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
            messages.success(request, 'Note created successfully.')
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