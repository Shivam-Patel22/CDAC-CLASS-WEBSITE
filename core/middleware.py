import re
from django.shortcuts import redirect
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that do not require authentication
        self.exceptions = [
            re.compile(r'^/$'),
            re.compile(r'^/login/'),
            re.compile(r'^/register/'),
            re.compile(r'^/guest-login/'),
            re.compile(r'^/logout/'),
            re.compile(r'^/admin-panel/login/'),
            re.compile(r'^/django-admin/'),
            re.compile(r'^/static/'),
            re.compile(r'^/media/'),
            re.compile(r'^/contact/'),
            re.compile(r'^/about/'),
            re.compile(r'^/courses/'),
            re.compile(r'^/certificates/'),
            re.compile(r'^/verify-certificate/'),
            re.compile(r'^/verify/'),
        ]

    def __call__(self, request):
        path = request.path_info

        # Allow requests that match exception paths
        for exception in self.exceptions:
            if exception.match(path):
                return self.get_response(request)

        # Allow requests if the user is authenticated or has a guest session
        if request.user.is_authenticated or request.session.get('is_guest'):
            return self.get_response(request)

        # Redirect unauthenticated requests for admin panel
        if path.startswith('/admin-panel/'):
            return redirect(reverse('dashboard:login'))

        # Redirect unauthenticated requests to the student login page with next param
        return redirect(f"{reverse('accounts:login')}?next={path}")
