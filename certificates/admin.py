from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student_name', 'course', 'issue_date', 'grade')
    search_fields = ('certificate_id', 'student_name')
    list_filter = ('issue_date', 'course')
    readonly_fields = ('certificate_id', 'created_at')
