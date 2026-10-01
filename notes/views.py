# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Note, NoteAttachment
from django.core.paginator import Paginator 
from accounts.models import User
from .forms import NoteForm
from django.db.models import Q
from datetime import datetime

#Para eliminar los archivos mediante JS
from django.http import JsonResponse
from django.views.decorators.http import require_POST

#Modelo CustomUser para traer a los proveedores
from accounts.models import User

#Librerias para exportar a excel
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.http import HttpResponse
from openpyxl.utils import get_column_letter

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
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.supplier = request.user
            note.save()
            
            # GUARDAR MÚLTIPLES ARCHIVOS
            files = request.FILES.getlist('attachments')
            for f in files:
                NoteAttachment.objects.create(note=note, file=f)
            
            messages.success(request, 'Nota creada con éxito.')
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
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            
            # AGREGAR NUEVOS ARCHIVOS (sin borrar los existentes)
            files = request.FILES.getlist('attachments')
            for f in files:
                NoteAttachment.objects.create(note=note, file=f)
            
            messages.success(request, 'Nota actualizada correctamente.')
            return redirect('supplier_dashboard')
    else:
        form = NoteForm(instance=note)
    
    return render(request, 'notes/note_form.html', {
        'form': form, 
        'action': 'Edit', 
        'note': note
    })


@login_required
@supplier_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, supplier=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully.')
        return redirect('supplier_dashboard')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
@require_POST
def delete_attachment(request, attachment_id):
    try:
        attachment = get_object_or_404(NoteAttachment, id=attachment_id)
        
        # Verificar permisos
        if request.user != attachment.note.supplier and not getattr(request.user, 'is_supervisor', False):
            return JsonResponse({
                'success': False, 
                'error': 'No tienes permiso para eliminar este archivo.'
            }, status=403)
        
        # Eliminar (Django borra automáticamente el archivo físico)
        attachment.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Archivo eliminado correctamente.'
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # Esto mostrará el error real en la terminal
        return JsonResponse({
            'success': False, 
            'error': f'Error interno: {str(e)}'
        }, status=500)

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


def is_supervisor(user):
    return user.is_authenticated and user.is_supervisor

#Funcion(Vista para exportar a Excel)
@login_required
@user_passes_test(is_supervisor, login_url='login')
def export_notes_excel(request):
    # 1. Obtener todas las notas
    notes = Note.objects.select_related('supplier').order_by('-created_at')
    
    # 2. Aplicar los mismos filtros que la tabla
    supplier_filter = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if supplier_filter:
        notes = notes.filter(supplier_id=supplier_filter)
    if date_from:
        notes = notes.filter(created_at__date__gte=date_from)
    if date_to:
        notes = notes.filter(created_at__date__lte=date_to)
    
    # 3. Crear el libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Notas"
    
    # 4. Estilos
    header_font = Font(name='Arial', bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='2563EB', end_color='2563EB', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    cell_alignment = Alignment(vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 5. Encabezados
    headers = ['Proveedor', 'Cédula/RIF', 'Categoría', 'Título', 'Contenido', 'Fecha de Creación', 'Fecha de Modificación']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # 6. Datos (Blindado contra errores de atributos)
    for row_num, note in enumerate(notes, 2):
        supplier = note.supplier
        
        # Obtener nombre de forma segura
        supplier_name = str(getattr(supplier, 'first_name', '') or str(supplier))
        
        # Obtener Cédula/RIF
        supplier_tax_id = str(supplier.document_id)        
        # Obtener categoría de forma segura
        if hasattr(note, 'get_category_display'):
            category = str(note.get_category_display())
        else:
            category = str(getattr(note, 'category', 'N/A'))
            
        row_data = [
            supplier_name,
            supplier_tax_id,
            category,
            str(note.title) if note.title else '',
            str(note.content) if note.content else '',
            note.created_at.strftime('%d/%m/%Y %H:%M') if note.created_at else '',
            note.updated_at.strftime('%d/%m/%Y %H:%M') if note.updated_at else '',
        ]
        
        for col_num, value in enumerate(row_data, 1):
            # Forzamos que el valor sea un string para que openpyxl no falle
            safe_value = str(value) if value is not None else ''
            cell = ws.cell(row=row_num, column=col_num, value=safe_value)
            cell.alignment = cell_alignment
            cell.border = thin_border
    
    # 7. Ajustar ancho de columnas
    column_widths = [20, 18, 15, 30, 50, 20, 20]
    for col_num, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(col_num)].width = width
    
    # 8. Congelar la primera fila
    ws.freeze_panes = 'A2'
    
    # 9. Crear la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_notas.xlsx"'
    
    wb.save(response)
    return response