from django.db import models
from courses.models import Course

class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    subject = models.CharField(max_length=200, default="General Inquiry")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Inquiry'
        verbose_name_plural = 'Customer Inquiries'

    def __str__(self):
        return f"Inquiry from {self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class AboutContent(models.Model):
    heading = models.CharField(max_length=200, default="About C-DAC")
    subtitle = models.CharField(max_length=300, default="Dedicated to excellence in practical computer education, advanced computing research, and skills training.")
    mission_title = models.CharField(max_length=150, default="Our Mission")
    description = models.TextField(default="At the Centre for Development of Advanced Computing (C-DAC), our mission is to carry out R&D in IT, Electronics and associated areas, empowering students and professionals with high-end IT education. Whether you are looking to start a career in software development, web engineering, database administration, or advanced computing, our hands-on curriculum is designed to get you industry-ready.")
    
    feature_1_title = models.CharField(max_length=150, default="🎯 Practical Learning")
    feature_1_desc = models.TextField(default="Every course emphasizes real-world projects and coding exercises over passive lecture theory.")
    feature_2_title = models.CharField(max_length=150, default="🏆 Authentic Certification")
    feature_2_desc = models.TextField(default="Certificates issued by C-DAC feature unique cryptographic IDs verifiable by employers globally.")
    feature_3_title = models.CharField(max_length=150, default="👥 Community Support")
    feature_3_desc = models.TextField(default="Dedicated lab assistants, mentor hours, and career placement assistance for all active students.")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'About Page Content'
        verbose_name_plural = 'About Page Content'

    def __str__(self):
        return f"About Content (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class ContactContent(models.Model):
    phone = models.CharField(max_length=100, default="+91 (020) 2570-4100")
    email = models.EmailField(default="contact@cdac.in")
    address = models.TextField(default="Gandhinagar, Gujarat, India")
    working_hours = models.CharField(max_length=150, default="Mon - Sat: 9:00 AM - 6:00 PM")
    map_embed_url = models.URLField(blank=True, null=True, max_length=500, default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d471.09!2d72.6320823!3d23.1852315!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x395c2b921555555d%3A0x50e94504c763b697!2sCDAC%20Computer%20Class!5e0!3m2!1sen!2sin!4v1722593000000!5m2!1sen!2sin")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Details Content'
        verbose_name_plural = 'Contact Details Content'

    def __str__(self):
        return f"Contact Content (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
