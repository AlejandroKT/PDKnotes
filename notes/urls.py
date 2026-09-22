from django.urls import path
from . import views

urlpatterns = [
    # Supplier URLs
    path('supplier/dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('supplier/note/new/', views.note_create, name='note_create'),
    path('supplier/note/<int:pk>/', views.note_detail, name='note_detail'),
    path('supplier/note/<int:pk>/edit/', views.note_edit, name='note_edit'),
    path('supplier/note/<int:pk>/delete/', views.note_delete, name='note_delete'),

    # Supervisor URLs
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('supervisor/supplier/<int:supplier_id>/notes/', views.supervisor_supplier_notes, name='supervisor_supplier_notes'),
    path('supervisor/note/<int:pk>/', views.supervisor_note_detail, name='supervisor_note_detail'),
]