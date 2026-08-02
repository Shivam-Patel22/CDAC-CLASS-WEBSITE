from django.db import models
from django.utils import timezone
from .models import CourseOffer

def latest_offers(request):
    try:
        today = timezone.now().date()
        offers = CourseOffer.objects.filter(
            status='active'
        ).filter(
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=today)
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
        ).select_related('course').order_by('-priority', '-created_at')
        
        return {'latest_offers': list(offers)}
    except Exception:
        return {'latest_offers': []}
