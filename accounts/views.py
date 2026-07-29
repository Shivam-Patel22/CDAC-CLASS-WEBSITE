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

def _generate_unique_username(email, full_name=''):
    base = email.split('@')[0].strip().lower() if email else 'user'
    base = ''.join(e for e in base if e.isalnum() or e in ('_', '-')) or 'user'
    username = base
    counter = 1
    while User.objects.filter(username__iexact=username).exists():
        username = f"{base}{counter}"
        counter += 1
    return username

def auth_page(request, tab='login'):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:index')
        return redirect('accounts:dashboard')

    login_form = StudentLoginForm()
    signup_form = StudentRegistrationForm()
    active_tab = tab

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        # Infer action type if not explicitly set
        if not action_type:
            if 'full_name' in request.POST or 'confirm_password' in request.POST:
                action_type = 'register'
            else:
                action_type = 'login'

        if action_type == 'register':
            active_tab = 'register'
            signup_form = StudentRegistrationForm(request.POST)
            if signup_form.is_valid():
                full_name = signup_form.cleaned_data['full_name']
                email = signup_form.cleaned_data['email']
                username = signup_form.cleaned_data.get('username')
                phone = signup_form.cleaned_data.get('phone', '')
                password = signup_form.cleaned_data['password']

                if not username:
                    username = _generate_unique_username(email, full_name)

                first_name = full_name.split(' ')[0] if ' ' in full_name else full_name
                last_name = ' '.join(full_name.split(' ')[1:]) if ' ' in full_name else ''

                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
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

                messages.success(request, f"Registration successful! You can now log in.")
                return redirect('accounts:login')
            else:
                form = signup_form
        else: # login
            active_tab = 'login'
            login_form = StudentLoginForm(request.POST)
            identifier = request.POST.get('username_or_email') or request.POST.get('email', '') or request.POST.get('username', '')
            password = request.POST.get('password', '')

            if identifier and password:
                identifier = identifier.strip()
                user_obj = User.objects.filter(
                    Q(username__iexact=identifier) | Q(email__iexact=identifier)
                ).first()

                username_to_auth = user_obj.username if user_obj else identifier
                user = authenticate(request, username=username_to_auth, password=password)

                if user is not None and user.is_active:
                    auth_login(request, user)
                    if user.is_staff:
                        messages.success(request, f"Welcome back, Administrator {user.first_name or user.username}!")
                        return redirect('dashboard:index')
                    else:
                        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                        return redirect('accounts:dashboard')
                else:
                    messages.error(request, "Invalid email/username or password. Please check your credentials.")
            else:
                messages.error(request, "Please enter your email/username and password.")

    return render(request, 'accounts/auth.html', {
        'form': signup_form if active_tab == 'register' else login_form,
        'login_form': login_form,
        'signup_form': signup_form,
        'active_tab': active_tab,
    })

def login(request):
    tab = request.GET.get('tab', 'login')
    return auth_page(request, tab=tab)

def register(request):
    tab = request.GET.get('tab', 'register')
    return auth_page(request, tab=tab)

def logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

@login_required(login_url='accounts:login')
def dashboard(request):
    certificates = Certificate.objects.filter(student=request.user).select_related('course').order_by('-issue_date')
    return render(request, 'accounts/dashboard.html', {'certificates': certificates})
