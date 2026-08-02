from core.models import Inquiry

def inquiry_notifications(request):
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
        try:
            return {
                'unread_inquiries_count': Inquiry.objects.filter(is_read=False).count()
            }
        except Exception:
            return {'unread_inquiries_count': 0}
    return {'unread_inquiries_count': 0}
