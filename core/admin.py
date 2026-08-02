from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'subject', 'course', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at', 'course')
    search_fields = ('name', 'phone', 'email', 'message', 'subject')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)
