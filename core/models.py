from django.db import models
from courses.models import Course

class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    subject = models.CharField(max_length=200, default="General Inquiry")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Inquiry'
        verbose_name_plural = 'Customer Inquiries'

    def __str__(self):
        return f"Inquiry from {self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
