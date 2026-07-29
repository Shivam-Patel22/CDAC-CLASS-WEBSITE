from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'fee', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
