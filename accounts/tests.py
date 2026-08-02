from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import StudentProfile

class AccountsTestCase(TestCase):
    def test_successful_registration(self):
        url = reverse('accounts:register')
        data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('core:home'))
        
        user = User.objects.get(email='john@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        
        # Verify linked StudentProfile created
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.phone, '1234567890')

    def test_duplicate_email_rejection(self):
        User.objects.create_user(username='john@example.com', email='john@example.com', password='Password123!')
        url = reverse('accounts:register')
        data = {
            'full_name': 'John Duplicate',
            'email': 'john@example.com',
            'phone': '9876543210',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', "A user with this email address already exists.")

    def test_dashboard_redirects_anonymous_user(self):
        url = reverse('accounts:dashboard')
        response = self.client.get(url)
        expected_redirect = f"{reverse('accounts:login')}?next={url}"
        self.assertRedirects(response, expected_redirect)

    def test_admin_add_student_success(self):
        admin = User.objects.create_superuser(username='admin', email='admin@cdac.in', password='adminpassword123')
        self.client.login(username='admin', password='adminpassword123')

        add_url = reverse('dashboard:add_student')
        data = {
            'full_name': 'Rahul Sharma',
            'email': 'rahul@example.com',
            'phone': '9876543210',
            'is_active': '1',
        }
        response = self.client.post(add_url, data)
        self.assertRedirects(response, reverse('dashboard:active_students'))

        user = User.objects.get(email='rahul@example.com')
        self.assertEqual(user.first_name, 'Rahul')
        self.assertEqual(user.last_name, 'Sharma')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
