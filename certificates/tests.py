from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from courses.models import Course
from certificates.models import Certificate

class CertificatesTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Python Web Development',
            description='Learn Django & Python',
            duration='12 Weeks',
            fee=499.00
        )
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='Password123!'
        )
        self.valid_cert = Certificate.objects.create(
            certificate_id='CERT-2026-TEST01',
            student_name='Jane Student',
            student=self.student_user,
            course=self.course,
            issue_date=date(2026, 1, 15),
            grade='A+'
        )

    def test_valid_certificate_id_returns_match(self):
        url = reverse('certificates:verify')
        response = self.client.post(url, {'certificate_id': 'CERT-2026-TEST01'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/result.html')
        self.assertContains(response, 'Jane Student')
        self.assertContains(response, 'Python Web Development')

    def test_invalid_certificate_id_shows_error(self):
        url = reverse('certificates:verify')
        response = self.client.post(url, {'certificate_id': 'CERT-9999-INVALID'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/verify.html')
        self.assertContains(response, "No valid certificate found")

    def test_custom_certificate_id_issue(self):
        admin = User.objects.create_superuser(username='certadmin', email='certadmin@cdac.in', password='adminpassword123')
        self.client.login(username='certadmin', password='adminpassword123')

        add_url = reverse('dashboard:add_certificate')
        data = {
            'certificate_id': 'CERT-2026-HARSHAL01',
            'student_name': 'Harshal Chauhan',
            'course': self.course.id,
            'issue_date': '2026-08-02',
            'grade': 'A+',
        }
        response = self.client.post(add_url, data)
        self.assertRedirects(response, reverse('dashboard:manage_certificates'))
        self.assertTrue(Certificate.objects.filter(certificate_id='CERT-2026-HARSHAL01').exists())

