from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def staff_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff member.
    Redirects to /admin-panel/login/ if not staff.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        if not request.user.is_staff:
            messages.error(request, "Access denied. Only staff administrators can access the admin panel.")
            return redirect('dashboard:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
