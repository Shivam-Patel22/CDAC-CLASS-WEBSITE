from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import staff_required
from .forms import AdminLoginForm, AdminCourseForm, AdminCertificateForm, AdminOfferForm
from courses.models import Course, CourseOffer
from certificates.models import Certificate
from certificates.utils import generate_certificate_id

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
                messages.success(request, f"Logged in as staff administrator ({user.username}).")
                return redirect('dashboard:index')
            else:
                messages.error(request, "Invalid staff credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'dashboard/login.html', {'form': form})

@staff_required
def admin_logout(request):
    auth_logout(request)
    messages.info(request, "Staff administrator logged out.")
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
