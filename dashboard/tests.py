from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class DashboardTestCase(TestCase):
    def setUp(self):
        # Create non-staff student user
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='Password123!',
            is_staff=False
        )
        # Create staff admin user
        self.staff_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='Password123!',
            is_staff=True
        )

    def test_unauthenticated_request_redirects_to_login(self):
        url = reverse('dashboard:index')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('dashboard:login'))

    def test_non_staff_student_is_rejected(self):
        # Log in as non-staff student
        self.client.login(username='student@test.com', password='Password123!')
        url = reverse('dashboard:index')
        response = self.client.get(url)
        # Staff required decorator redirects non-staff user to dashboard:login with error message
        self.assertRedirects(response, reverse('dashboard:login'))

    def test_staff_admin_can_access_dashboard(self):
        self.client.login(username='admin@test.com', password='Password123!')
        url = reverse('dashboard:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')
