from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import StudentRegistrationForm, StudentLoginForm
from .models import StudentProfile
from certificates.models import Certificate

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            password = form.cleaned_data['password']

            first_name = full_name.split(' ')[0] if ' ' in full_name else full_name
            last_name = ' '.join(full_name.split(' ')[1:]) if ' ' in full_name else ''

            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=False,
                    is_superuser=False
                )
                StudentProfile.objects.create(
                    user=user,
                    phone=phone
                )

            messages.success(request, "Registration successful! You can now log in to access your student dashboard.")
            return redirect('accounts:login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Lookup username corresponding to email
            try:
                user_obj = User.objects.get(email__iexact=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = email

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_staff:
                    messages.warning(request, "Staff accounts must log in via the Staff Portal.")
                    return redirect('dashboard:login')
                
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = StudentLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:home')

@login_required(login_url='accounts:login')
def dashboard(request):
    # Rule 3: Strictly query Certificate.objects.filter(student=request.user)
    certificates = Certificate.objects.filter(student=request.user).select_related('course').order_by('-issue_date')
    return render(request, 'accounts/dashboard.html', {'certificates': certificates})
