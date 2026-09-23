# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .forms import SupplierRegistrationForm, CustomAuthenticationForm,SupplierProfileForm
from django.core.exceptions import PermissionDenied
from .models import User



def register_view(request):
    if request.user.is_authenticated:
        return redirect('supplier_dashboard')
        
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_supplier = True
            user.is_supervisor = False
            user.save()
            messages.success(request, 'Registro exitoso. Porfavor ingrese.')
            return redirect('login')
    else:
        form = SupplierRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_supervisor:
            return redirect('supervisor_dashboard')
        return redirect('supplier_dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            document_id = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(document_id=document_id, password=password)
            if user is not None:
                login(request, user)
                if user.is_supervisor:
                    return redirect('supervisor_dashboard')
                return redirect('supplier_dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def supplier_profile(request, pk):
    # Obtenemos el usuario del perfil, asegurándonos de que sea un proveedor
    profile_user = get_object_or_404(User, pk=pk, is_supplier=True)
    
    # SEGURIDAD: Si soy proveedor, solo puedo ver mi propio perfil
    if request.user.is_supplier and request.user.pk != profile_user.pk:
        raise PermissionDenied("No tienes permiso para ver este perfil.")
        
    # Determinamos si el formulario será editable
    is_editable = request.user.is_supplier and request.user.pk == profile_user.pk
    
    # Procesamos el formulario si es POST y es editable
    if request.method == 'POST' and is_editable:
        form = SupplierProfileForm(request.POST, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('supplier_profile', pk=profile_user.pk)
    else:
        form = SupplierProfileForm(instance=profile_user)
        
    return render(request, 'accounts/supplier_profile.html', {
        'profile_user': profile_user,
        'form': form,
        'is_editable': is_editable
    })