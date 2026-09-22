from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SupplierRegistrationForm, CustomAuthenticationForm

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
            messages.success(request, 'Registration successful. Please log in.')
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