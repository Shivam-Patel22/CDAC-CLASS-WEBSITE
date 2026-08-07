from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from courses.models import Course

def home(request):
    try:
        featured_courses = Course.objects.filter(is_featured=True).order_by('-created_at')[:3]
        if not featured_courses.exists():
            featured_courses = Course.objects.all().order_by('-created_at')[:3]
    except Exception:
        featured_courses = []
        
    context = {
        'featured_courses': featured_courses,
    }
    return render(request, 'core/home.html', context)

from .models import Inquiry, AboutContent, ContactContent
from dashboard.forms import AdminAboutForm, AdminContactForm

def about(request):
    about_content = AboutContent.get_solo()
    about_form = None
    if request.user.is_authenticated and request.user.is_staff:
        about_form = AdminAboutForm(instance=about_content)
    return render(request, 'core/about.html', {
        'about_content': about_content,
        'about_form': about_form
    })

def contact(request):
    contact_content = ContactContent.get_solo()
    contact_form = None
    if request.user.is_authenticated and request.user.is_staff:
        contact_form = AdminContactForm(instance=contact_content)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data.get('email', '')
            course = form.cleaned_data.get('course')
            course_name = course.name if course else "General Inquiry"
            message_text = form.cleaned_data.get('message', '')
            
            # Save inquiry in database for Admin Panel notification
            Inquiry.objects.create(
                name=name,
                phone=phone,
                email=email,
                course=course,
                subject=f"Inquiry: {course_name}",
                message=message_text
            )
            
            # Print inquiry details to console
            print(f"[COURSE INQUIRY] From: {name} | Phone: {phone} | Course: {course_name}\nMessage: {message_text}")
            
            messages.success(request, f"Thank you, {name}! Your inquiry has been received. We will get back to you shortly.")
            return redirect('core:contact')
    else:
        initial_data = {}
        course_param = request.GET.get('course')
        if course_param:
            if str(course_param).isdigit():
                initial_data['course'] = str(course_param)
            else:
                matched_course = Course.objects.filter(name__icontains=course_param).first()
                if matched_course:
                    initial_data['course'] = str(matched_course.id)
        form = ContactForm(initial=initial_data)
    
    return render(request, 'core/contact.html', {
        'form': form,
        'contact_content': contact_content,
        'contact_form': contact_form
    })
