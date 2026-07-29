from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
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
            username = form.cleaned_data.get('username')
            email = form.cleaned_data['email']
            phone = form.cleaned_data.get('phone', '')
            password = form.cleaned_data['password']
            role = request.POST.get('role', 'user')

            # Default username to email if not explicitly provided
            if not username:
                username = email

            first_name = full_name.split(' ')[0] if ' ' in full_name else full_name
            last_name = ' '.join(full_name.split(' ')[1:]) if ' ' in full_name else ''
            is_staff_user = (role == 'admin')

            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=is_staff_user,
                    is_superuser=False
                )
                StudentProfile.objects.create(
                    user=user,
                    phone=phone
                )

            messages.success(
                request, 
                f"Registration successful as {'Admin' if is_staff_user else 'User'}! You can now log in."
            )
            return redirect('accounts:login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:index')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        identifier = request.POST.get('username_or_email') or request.POST.get('email', '')
        password = request.POST.get('password', '')
        selected_role = request.POST.get('role', 'user')

        if identifier and password:
            # Lookup user by username OR email
            user_obj = User.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            ).first()

            username_to_auth = user_obj.username if user_obj else identifier
            user = authenticate(request, username=username_to_auth, password=password)

            if user is not None:
                auth_login(request, user)
                role_title = "Admin" if user.is_staff else "User/Student"
                messages.success(request, f"Welcome back, {user.first_name or user.username}! Logged in as {role_title}.")
                
                if user.is_staff or selected_role == 'admin':
                    return redirect('dashboard:index')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Invalid email/username or password.")
        else:
            messages.error(request, "Please enter your email/username and password.")
    else:
        form = StudentLoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:home')

@login_required(login_url='accounts:login')
def dashboard(request):
    certificates = Certificate.objects.filter(student=request.user).select_related('course').order_by('-issue_date')
    return render(request, 'accounts/dashboard.html', {'certificates': certificates})
