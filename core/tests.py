from django.test import TestCase
from django.urls import reverse
from courses.models import Course

class CoreTestCase(TestCase):
    def setUp(self):
        self.course1 = Course.objects.create(name="Python Web Development", description="Learn Django & Python", duration="3 Months")
        self.course2 = Course.objects.create(name="Data Science Fundamentals", description="Learn Data Science", duration="6 Months")

    def test_contact_page_renders_with_courses(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Full Name *")
        self.assertContains(response, "Phone Number *")
        self.assertContains(response, "Interested in Course")
        self.assertContains(response, "Python Web Development")
        self.assertContains(response, "Data Science Fundamentals")

    def test_contact_page_preselects_course_from_query_param(self):
        response = self.client.get(f"{reverse('core:contact')}?course={self.course1.id}")
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.initial.get('course'), str(self.course1.id))

    def test_contact_form_submission(self):
        from core.models import Inquiry
        data = {
            'name': 'Jane Student',
            'phone': '9876543210',
            'course': self.course1.id,
            'message': 'I would like to inquire about course fees and batch timings.',
        }
        response = self.client.post(reverse('core:contact'), data)
        self.assertRedirects(response, reverse('core:contact'))

        # Verify inquiry saved in database
        self.assertEqual(Inquiry.objects.count(), 1)
        inquiry = Inquiry.objects.first()
        self.assertEqual(inquiry.name, 'Jane Student')
        self.assertEqual(inquiry.phone, '9876543210')
        self.assertEqual(inquiry.course, self.course1)
        self.assertFalse(inquiry.is_read)

    def test_contact_form_submission_without_message(self):
        from core.models import Inquiry
        data = {
            'name': 'Bob Student',
            'phone': '9876543211',
            'course': self.course1.id,
            'message': '',
        }
        response = self.client.post(reverse('core:contact'), data)
        self.assertRedirects(response, reverse('core:contact'))

        self.assertEqual(Inquiry.objects.count(), 1)
        inquiry = Inquiry.objects.first()
        self.assertEqual(inquiry.name, 'Bob Student')
        self.assertEqual(inquiry.message, '')

