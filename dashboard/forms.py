from django import forms
from django.contrib.auth.models import User
from courses.models import Course
from certificates.models import Certificate
from certificates.utils import generate_certificate_id

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Staff Username or Email', 'required': 'required'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': 'required'})
    )

class AdminCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'duration', 'fee', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Name', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Detailed syllabus and overview', 'rows': 5, 'required': 'required'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8 Weeks / 3 Months', 'required': 'required'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee amount (e.g. 299.00)', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AdminCertificateForm(forms.ModelForm):
    # Optional link to registered student user
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=False).order_by('first_name', 'username'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="— Select Registered Student (Optional) —"
    )

    class Meta:
        model = Certificate
        fields = ['certificate_id', 'student_name', 'student', 'course', 'issue_date', 'grade']
        widgets = {
            'certificate_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Full Name', 'required': 'required'}),
            'course': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grade A / Pass'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If adding a new certificate, pre-populate certificate_id with generated value
        if not self.instance.pk and not self.initial.get('certificate_id'):
            self.initial['certificate_id'] = generate_certificate_id()
