from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# accounts/admin.py

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('document_id', 'first_name', 'is_supplier', 'is_supervisor', 'is_staff')
    list_filter = ('is_supplier', 'is_supervisor', 'is_staff')
    search_fields = ('document_id', 'first_name')
    ordering = ('document_id',)
    
    fieldsets = (
        (None, {'fields': ('document_id', 'password')}),
        ('Personal info', {'fields': ('first_name', 'email')}),
        ('Permissions', {'fields': ('is_supplier', 'is_supervisor', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('document_id', 'first_name', 'password1', 'password2', 'is_supplier', 'is_supervisor', 'is_staff'),
        }),
    )