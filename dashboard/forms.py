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
    class Meta:
        model = Certificate
        fields = ['certificate_id', 'student_name', 'course', 'issue_date', 'grade']
        widgets = {
            'certificate_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Full Name', 'required': 'required'}),
            'course': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1000-01-01', 'max': '9999-12-31', 'required': 'required'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grade A / Pass'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If adding a new certificate, pre-populate certificate_id with generated value
        if not self.instance.pk and not self.initial.get('certificate_id'):
            self.initial['certificate_id'] = generate_certificate_id()

    def clean_issue_date(self):
        issue_date = self.cleaned_data.get('issue_date')
        if issue_date:
            if issue_date.year < 1000 or issue_date.year > 9999:
                raise forms.ValidationError("Please enter a valid 4-digit year (1000–9999).")
        return issue_date

    def clean_certificate_id(self):
        cert_id = self.cleaned_data.get('certificate_id', '').strip()
        if not cert_id:
            cert_id = generate_certificate_id()

        qs = Certificate.objects.filter(certificate_id__iexact=cert_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Certificate ID '{cert_id}' is already in use. Please enter a unique Certificate ID.")
        return cert_id

from courses.models import CourseOffer

class AdminOfferForm(forms.ModelForm):
    class Meta:
        model = CourseOffer
        fields = ['title', 'description', 'course', 'discount', 'badge', 'start_date', 'end_date', 'priority', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 30% OFF on Python Course', 'required': 'required', 'id': 'id_title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Offer overview & terms', 'rows': 3}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'discount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 30% OFF / ₹999 Only', 'id': 'id_discount'}),
            'badge': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 🎉 SPECIAL OFFER', 'id': 'id_badge'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1000-01-01', 'max': '9999-12-31'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1000-01-01', 'max': '9999-12-31'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class AdminStudentForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name (e.g. Rahul Sharma)', 'required': 'required'})
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username (Optional, auto-generated if blank)'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address', 'required': 'required'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Optional)'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all().order_by('name'),
        required=False,
        empty_label="— Select Enrolled Course (Optional) —",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_joined = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '1000-01-01', 'max': '9999-12-31'})
    )
    is_active = forms.ChoiceField(
        choices=[('1', 'Active'), ('0', 'Inactive')],
        initial='1',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional internal notes...', 'rows': 2})
    )

from core.models import AboutContent, ContactContent

class AdminAboutForm(forms.ModelForm):
    class Meta:
        model = AboutContent
        fields = ['heading', 'subtitle', 'mission_title', 'description', 'feature_1_title', 'feature_1_desc', 'feature_2_title', 'feature_2_desc', 'feature_3_title', 'feature_3_desc']
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'mission_title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'feature_1_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature_1_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'feature_2_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature_2_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'feature_3_title': forms.TextInput(attrs={'class': 'form-control'}),
            'feature_3_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class AdminContactForm(forms.ModelForm):
    class Meta:
        model = ContactContent
        fields = ['phone', 'email', 'address', 'working_hours', 'map_embed_url']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'required'}),
            'working_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'map_embed_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Google Maps Embed URL'}),
        }
