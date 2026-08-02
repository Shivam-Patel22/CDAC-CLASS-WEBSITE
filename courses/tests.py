from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from courses.models import Course, CourseOffer

class CourseOfferTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(name="Python Masterclass", description="Python basics", duration="2 Months")
        self.today = timezone.now().date()

        self.active_offer = CourseOffer.objects.create(
            title="30% OFF on Python",
            badge="🎉 SPECIAL OFFER",
            discount="30% OFF",
            course=self.course,
            status="active"
        )
        self.scheduled_offer = CourseOffer.objects.create(
            title="Future Batch Discount",
            start_date=self.today + timedelta(days=5),
            status="active"
        )
        self.expired_offer = CourseOffer.objects.create(
            title="Old Summer Sale",
            end_date=self.today - timedelta(days=2),
            status="active"
        )
        self.inactive_offer = CourseOffer.objects.create(
            title="Draft Offer",
            status="inactive"
        )

    def test_offer_computed_statuses(self):
        self.assertEqual(self.active_offer.computed_status, "Active")
        self.assertEqual(self.scheduled_offer.computed_status, "Scheduled")
        self.assertEqual(self.expired_offer.computed_status, "Expired")
        self.assertEqual(self.inactive_offer.computed_status, "Inactive")

    def test_is_currently_active(self):
        self.assertTrue(self.active_offer.is_currently_active)
        self.assertFalse(self.scheduled_offer.is_currently_active)
        self.assertFalse(self.expired_offer.is_currently_active)
        self.assertFalse(self.inactive_offer.is_currently_active)

    def test_ticker_context_processor_filters_only_active_offers(self):
        session = self.client.session
        session['is_guest'] = True
        session.save()
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        ticker_offers = response.context['latest_offers']
        self.assertIn(self.active_offer, ticker_offers)
        self.assertNotIn(self.scheduled_offer, ticker_offers)
        self.assertNotIn(self.expired_offer, ticker_offers)
        self.assertNotIn(self.inactive_offer, ticker_offers)
