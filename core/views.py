from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from courses.models import Course

def home(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    try:
        featured_courses = Course.objects.all().order_by('-created_at')[:3]
    except Exception:
        featured_courses = []
    return render(request, 'core/home.html', {'featured_courses': featured_courses})

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data.get('subject', 'General Inquiry')
            message_text = form.cleaned_data['message']
            
            # Print message to console per spec
            print(f"[CONTACT FORM] From: {name} <{email}> | Subject: {subject}\nMessage: {message_text}")
            
            messages.success(request, f"Thank you, {name}! Your message has been received. We will get back to you shortly.")
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})
