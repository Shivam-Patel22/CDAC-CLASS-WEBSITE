from django.db import models
from django.contrib.auth.models import User

class Certificate(models.Model):
    certificate_id = models.CharField(max_length=30, unique=True, db_index=True)
    student_name = models.CharField(max_length=200)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.PROTECT)
    issue_date = models.DateField()
    grade = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.certificate_id} - {self.student_name} ({self.course.name})"
