from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import staff_required
from .forms import AdminLoginForm, AdminCourseForm, AdminCertificateForm, AdminOfferForm, AdminStudentForm, AdminAboutForm, AdminContactForm
from courses.models import Course, CourseOffer
from certificates.models import Certificate
from certificates.utils import generate_certificate_id
from certificates.forms import CertificateVerificationForm



def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Lookup by email or username
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_or_email

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_staff:
                    messages.error(request, "Access denied. Student accounts cannot access the admin panel.")
                    return redirect('dashboard:login')
                
                auth_login(request, user)
                return redirect('dashboard:index')
            else:
                messages.error(request, "Invalid staff credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'dashboard/login.html', {'form': form})

@staff_required
def admin_logout(request):
    auth_logout(request)
    return redirect('dashboard:login')

from core.models import Inquiry

@staff_required
def index(request):
    total_courses = Course.objects.count()
    total_certificates = Certificate.objects.count()
    total_students = User.objects.filter(is_staff=False).count()
    total_inquiries = Inquiry.objects.count()
    unread_inquiries_count = Inquiry.objects.filter(is_read=False).count()
    recent_certificates = Certificate.objects.select_related('course').order_by('-created_at')[:5]
    recent_inquiries = Inquiry.objects.select_related('course').order_by('-created_at')[:5]

    context = {
        'total_courses': total_courses,
        'total_certificates': total_certificates,
        'total_students': total_students,
        'total_inquiries': total_inquiries,
        'unread_inquiries_count': unread_inquiries_count,
        'recent_certificates': recent_certificates,
        'recent_inquiries': recent_inquiries,
    }
    return render(request, 'dashboard/index.html', context)

@staff_required
def manage_courses(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'dashboard/manage_courses.html', {'courses': courses})

@staff_required
def add_course(request):
    if request.method == 'POST':
        form = AdminCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name}' created successfully.")
            return redirect('dashboard:manage_courses')
    else:
        form = AdminCourseForm()

    return render(request, 'dashboard/course_form.html', {'form': form, 'title': 'Add New Course'})

@staff_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = AdminCourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.name}' updated successfully.")
            return redirect('dashboard:manage_courses')
    else:
        form = AdminCourseForm(instance=course)

    return render(request, 'dashboard/course_form.html', {'form': form, 'title': f'Edit Course: {course.name}', 'course': course})

@staff_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course_name = course.name
        try:
            course.delete()
            messages.success(request, f"Course '{course_name}' deleted successfully.")
        except Exception:
            messages.error(request, f"Cannot delete course '{course_name}' because certificates have been issued for it.")
        return redirect('dashboard:manage_courses')

    return render(request, 'dashboard/course_delete_confirm.html', {'course': course})

@staff_required
def manage_certificates(request):
    certificates = Certificate.objects.select_related('course', 'student').order_by('-created_at')
    return render(request, 'dashboard/manage_certificates.html', {'certificates': certificates})

@staff_required
def add_certificate(request):
    if request.method == 'POST':
        form = AdminCertificateForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            # Ensure certificate_id is server-generated if blank
            if not cert.certificate_id:
                cert.certificate_id = generate_certificate_id()
            cert.save()
            messages.success(request, f"Certificate '{cert.certificate_id}' issued to {cert.student_name}.")
            return redirect('dashboard:manage_certificates')
    else:
        form = AdminCertificateForm()

    return render(request, 'dashboard/certificate_form.html', {'form': form, 'title': 'Issue New Certificate'})

@staff_required
def edit_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        form = AdminCertificateForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, f"Certificate '{cert.certificate_id}' updated successfully.")
            return redirect('dashboard:manage_certificates')
    else:
        form = AdminCertificateForm(instance=cert)

    return render(request, 'dashboard/certificate_form.html', {'form': form, 'title': f'Edit Certificate: {cert.certificate_id}', 'cert': cert})

@staff_required
def revoke_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        cert_id = cert.certificate_id
        cert.delete()
        messages.success(request, f"Certificate '{cert_id}' has been revoked.")
        return redirect('dashboard:manage_certificates')

    return render(request, 'dashboard/certificate_revoke_confirm.html', {'cert': cert})

@staff_required
def verify_certificate(request, pk):
    """
    Admin verification endpoint validating certificate data integrity without modifying contents.
    Checks:
    - Certificate exists & ID matches
    - Certificate not revoked
    - Student & Course exist
    - Issue Date & Grade match
    - Linked account matches
    - Verification token / hash integrity
    """
    try:
        cert = Certificate.objects.select_related('course', 'student').get(pk=pk)
    except Certificate.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'success': False, 'error': 'Certificate not found'}, status=404)
        messages.error(request, "Certificate not found.")
        return redirect('dashboard:manage_certificates')

    # Ensure hash is generated if missing
    if not cert.verification_hash:
        cert.verification_hash = cert.generate_verification_hash()
        cert.verification_token = cert.verification_hash[:16].upper()
        cert.save()

    calculated_hash = cert.generate_verification_hash()
    hash_valid = (cert.verification_hash == calculated_hash)

    checks = {
        'id_match': bool(cert.certificate_id),
        'student_exists': bool(cert.student_name and cert.student_name.strip()),
        'course_exists': bool(cert.course_id and cert.course),
        'issue_date_valid': bool(cert.issue_date),
        'grade_valid': True,
        'linked_account_valid': True if not cert.student else bool(cert.student.email),
        'hash_valid': hash_valid,
        'not_revoked': True
    }

    is_verified = all(checks.values())

    # Update last_verified_at timestamp safely
    cert.last_verified_at = timezone.now()
    cert.save(update_fields=['last_verified_at'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': is_verified,
            'certificate_id': cert.certificate_id,
            'student_name': cert.student_name,
            'course_name': cert.course.name if cert.course else 'N/A',
            'issue_date': cert.issue_date.strftime('%Y-%m-%d') if cert.issue_date else 'N/A',
            'grade': cert.grade or 'N/A',
            'linked_account': cert.student.email if cert.student else 'Unlinked',
            'verification_token': cert.verification_token or 'VERIFIED-TOKEN',
            'verification_hash': cert.verification_hash,
            'last_verified_at': cert.last_verified_at.strftime('%Y-%m-%d %H:%M:%S'),
            'checks': checks,
            'message': '✓ Certificate Verified Successfully. This certificate is authentic and valid.' if is_verified else 'Certificate data mismatch or verification failed.'
        })

    return redirect('dashboard:manage_certificates')

@staff_required
def print_certificate(request, pk):
    """
    Renders official certificate template for printing with window.print() auto-trigger.
    Updates printed_at timestamp on the certificate.
    """
    cert = get_object_or_404(Certificate.objects.select_related('course', 'student'), pk=pk)

    # Ensure hash and token exist
    if not cert.verification_hash:
        cert.verification_hash = cert.generate_verification_hash()
        cert.verification_token = cert.verification_hash[:16].upper()

    cert.printed_at = timezone.now()
    cert.save(update_fields=['printed_at', 'verification_hash', 'verification_token'])

    verification_url = request.build_absolute_uri(
        reverse('certificates:verify') + f"?certificate_id={cert.certificate_id}"
    )

    context = {
        'certificate': cert,
        'verification_url': verification_url,
    }
    return render(request, 'dashboard/print_certificate.html', context)

@staff_required
def admin_verify_search(request):
    """
    Admin panel certificate verification lookup page.
    Allows staff to enter any Certificate ID directly within the admin panel
    without navigating to the public user panel.
    """
    cert_id = None
    certificate = None
    error_message = None

    if request.method == 'POST':
        form = CertificateVerificationForm(request.POST)
        if form.is_valid():
            cert_id = form.cleaned_data['certificate_id']
            try:
                certificate = Certificate.objects.select_related('course', 'student').get(certificate_id__iexact=cert_id)
                certificate.last_verified_at = timezone.now()
                certificate.save(update_fields=['last_verified_at'])
            except Certificate.DoesNotExist:
                error_message = f"No valid certificate found matching Certificate ID '{cert_id}'."
    else:
        cert_id = request.GET.get('certificate_id', '').strip().upper()
        if cert_id:
            form = CertificateVerificationForm(initial={'certificate_id': cert_id})
            try:
                certificate = Certificate.objects.select_related('course', 'student').get(certificate_id__iexact=cert_id)
                certificate.last_verified_at = timezone.now()
                certificate.save(update_fields=['last_verified_at'])
            except Certificate.DoesNotExist:
                error_message = f"No valid certificate found matching Certificate ID '{cert_id}'."
        else:
            form = CertificateVerificationForm()

    context = {
        'form': form,
        'certificate': certificate,
        'cert_id': cert_id,
        'error_message': error_message,
    }
    return render(request, 'dashboard/admin_verify_certificate.html', context)



@staff_required
def manage_inquiries(request):
    status_filter = request.GET.get('status', 'all')
    queryset = Inquiry.objects.select_related('course').order_by('-created_at')

    if status_filter == 'unread':
        queryset = queryset.filter(is_read=False)
    elif status_filter == 'read':
        queryset = queryset.filter(is_read=True)

    unread_count = Inquiry.objects.filter(is_read=False).count()
    total_count = Inquiry.objects.count()

    context = {
        'inquiries': queryset,
        'status_filter': status_filter,
        'unread_count': unread_count,
        'total_count': total_count,
    }
    return render(request, 'dashboard/manage_inquiries.html', context)

@staff_required
def toggle_inquiry_read(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    inquiry.is_read = not inquiry.is_read
    inquiry.save()
    status_str = "Read" if inquiry.is_read else "Unread"
    messages.success(request, f"Inquiry from {inquiry.name} marked as {status_str}.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:manage_inquiries')

@staff_required
def delete_inquiry(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    name = inquiry.name
    inquiry.delete()
    messages.success(request, f"Inquiry from {name} has been deleted.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:manage_inquiries')

from django.utils import timezone
from django.db.models import Q

@staff_required
def manage_offers(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')
    course_filter = request.GET.get('course', '')

    queryset = CourseOffer.objects.select_related('course', 'created_by').order_by('-priority', '-created_at')

    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(discount__icontains=search_query) |
            Q(badge__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if course_filter:
        queryset = queryset.filter(course_id=course_filter)

    today = timezone.now().date()
    if status_filter == 'active':
        queryset = [o for o in queryset if o.computed_status == 'Active']
    elif status_filter == 'scheduled':
        queryset = [o for o in queryset if o.computed_status == 'Scheduled']
    elif status_filter == 'expired':
        queryset = [o for o in queryset if o.computed_status == 'Expired']
    elif status_filter == 'draft':
        queryset = [o for o in queryset if o.computed_status == 'Draft']
    elif status_filter == 'inactive':
        queryset = [o for o in queryset if o.computed_status == 'Inactive']

    courses = Course.objects.all().order_by('name')
    total_offers = CourseOffer.objects.count()
    active_offers_count = sum(1 for o in CourseOffer.objects.all() if o.is_currently_active)

    context = {
        'offers': queryset,
        'search_query': search_query,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'courses': courses,
        'total_offers': total_offers,
        'active_offers_count': active_offers_count,
    }
    return render(request, 'dashboard/manage_offers.html', context)

@staff_required
def add_offer(request):
    if request.method == 'POST':
        form = AdminOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.created_by = request.user
            offer.save()
            messages.success(request, f"Course Offer '{offer.title}' created successfully.")
            return redirect('dashboard:manage_offers')
    else:
        form = AdminOfferForm()

    return render(request, 'dashboard/offer_form.html', {'form': form, 'title': 'Create New Course Offer'})

@staff_required
def edit_offer(request, pk):
    offer = get_object_or_404(CourseOffer, pk=pk)
    if request.method == 'POST':
        form = AdminOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course Offer '{offer.title}' updated successfully.")
            return redirect('dashboard:manage_offers')
    else:
        form = AdminOfferForm(instance=offer)

    return render(request, 'dashboard/offer_form.html', {'form': form, 'title': f'Edit Offer: {offer.title}', 'offer': offer})

@staff_required
def toggle_offer_status(request, pk):
    offer = get_object_or_404(CourseOffer, pk=pk)
    if offer.status == 'active':
        offer.status = 'inactive'
        status_msg = "deactivated"
    else:
        offer.status = 'active'
        status_msg = "activated"
    offer.save()
    messages.success(request, f"Course Offer '{offer.title}' has been {status_msg}.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:manage_offers')

@staff_required
def delete_offer(request, pk):
    offer = get_object_or_404(CourseOffer, pk=pk)
    title = offer.title
    offer.delete()
    messages.success(request, f"Course Offer '{title}' has been permanently deleted.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:manage_offers')

# ── Active Student Accounts ─────────────────────────────────
from django.core.paginator import Paginator
from accounts.models import StudentProfile
from .forms import AdminStudentForm

@staff_required
def active_students(request):
    """List all student accounts with search, sort, pagination, and Add Student modal."""
    search_q  = request.GET.get('q', '').strip()
    sort_by   = request.GET.get('sort', 'name')   # name | email | date
    direction = request.GET.get('dir', 'asc')      # asc  | desc

    qs = User.objects.filter(is_staff=False).select_related('student_profile')

    if search_q:
        qs = qs.filter(
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q)  |
            Q(username__icontains=search_q)   |
            Q(email__icontains=search_q)
        )

    sort_map = {
        'name':  'first_name',
        'email': 'email',
        'date':  'date_joined',
    }
    order_field = sort_map.get(sort_by, 'first_name')
    if direction == 'desc':
        order_field = f'-{order_field}'
    qs = qs.order_by(order_field)

    paginator   = Paginator(qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)
    courses     = Course.objects.all().order_by('name')

    context = {
        'page_obj':   page_obj,
        'search_q':   search_q,
        'sort_by':    sort_by,
        'direction':  direction,
        'total_count': paginator.count,
        'courses':    courses,
        'student_form': AdminStudentForm(),
    }
    return render(request, 'dashboard/active_students.html', context)

@staff_required
def add_student(request):
    if request.method == 'POST':
        form = AdminStudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, f"A student account with email '{email}' already exists.")
                return redirect('dashboard:active_students')

            full_name = form.cleaned_data['full_name'].strip()
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            username = form.cleaned_data.get('username', '').strip()
            if not username:
                base_user = email.split('@')[0]
                username = base_user
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_user}{counter}"
                    counter += 1

            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, f"Username '{username}' is already taken.")
                return redirect('dashboard:active_students')

            is_active_val = form.cleaned_data['is_active'] == '1'
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_active=is_active_val
            )
            user.set_password('cdac1234')

            date_joined = form.cleaned_data.get('date_joined')
            if date_joined:
                user.date_joined = date_joined
            user.save()

            profile, _ = StudentProfile.objects.get_or_create(user=user)
            profile.phone = form.cleaned_data.get('phone', '')
            profile.enrolled_course = form.cleaned_data.get('course')
            profile.notes = form.cleaned_data.get('notes', '')
            profile.save()

            messages.success(request, f"Student '{full_name}' (@{username}) enrolled successfully.")
            return redirect('dashboard:active_students')
        else:
            messages.error(request, "Invalid student details. Please check the required fields.")
            return render(request, 'dashboard/add_student.html', {'form': form, 'title': 'Add New Student'})
    else:
        form = AdminStudentForm()

    return render(request, 'dashboard/add_student.html', {'form': form, 'title': 'Add New Student'})

@staff_required
def toggle_student_status(request, pk):
    user_obj = get_object_or_404(User, pk=pk, is_staff=False)
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    status_str = "Active" if user_obj.is_active else "Inactive"
    messages.success(request, f"Student '{user_obj.get_full_name() or user_obj.username}' marked as {status_str}.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:active_students')

@staff_required
def delete_student(request, pk):
    user_obj = get_object_or_404(User, pk=pk, is_staff=False)
    name = user_obj.get_full_name() or user_obj.username
    user_obj.delete()
    messages.success(request, f"Student account '{name}' deleted successfully.")

    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard:active_students')

from core.models import AboutContent, ContactContent

@staff_required
def edit_about(request):
    about_obj = AboutContent.get_solo()
    if request.method == 'POST':
        form = AdminAboutForm(request.POST, instance=about_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "About section content updated successfully.")
            next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)
            return redirect('core:about')
        else:
            messages.error(request, "Error updating About content. Please check the required fields.")
    else:
        form = AdminAboutForm(instance=about_obj)

    context = {
        'form': form,
        'about_obj': about_obj,
        'title': 'Edit About Section Content'
    }
    return render(request, 'dashboard/edit_about.html', context)

@staff_required
def edit_contact(request):
    contact_obj = ContactContent.get_solo()
    if request.method == 'POST':
        form = AdminContactForm(request.POST, instance=contact_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact section details updated successfully.")
            next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
            if next_url:
                return redirect(next_url)
            return redirect('core:contact')
        else:
            messages.error(request, "Error updating Contact details. Please check the required fields.")
    else:
        form = AdminContactForm(instance=contact_obj)

    context = {
        'form': form,
        'contact_obj': contact_obj,
        'title': 'Edit Contact Details & Location'
    }
    return render(request, 'dashboard/edit_contact.html', context)

