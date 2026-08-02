from datetime import date
from django.core.management.base import BaseCommand
from courses.models import Course
from certificates.models import Certificate
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seeds initial sample courses and certificates into the database'

    def handle(self, *args, **options):
        self.stdout.write("Seeding courses, certificates, and admin user...")

        # Create or update default Admin Staff user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cdac.in',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('adminpassword123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_status = "Created" if created else "Updated password for"
        self.stdout.write(f"Admin User: {admin_user.username} ({admin_status})")

        courses_data = [
            {
                'name': 'Python Web Development (Django & FastAPI)',
                'description': 'Master backend web development using Python, Django, REST APIs, and PostgreSQL. Build scalable real-world projects.',
                'duration': '3 Months',
                'fee': 15000.00
            },
            {
                'name': 'Full Stack Web Development (MERN Stack)',
                'description': 'Comprehensive training in React.js, Node.js, Express, and MongoDB with modern frontend and API integration.',
                'duration': '6 Months',
                'fee': 25000.00
            },
            {
                'name': 'Data Science & Machine Learning',
                'description': 'Hands-on course covering Python for Data Analysis, Pandas, NumPy, Scikit-Learn, and Machine Learning models.',
                'duration': '4 Months',
                'fee': 20000.00
            },
            {
                'name': 'Certificate Course in Financial Accounting (Tally Prime & GST)',
                'description': 'Practical accounting training on Tally Prime, GST filing, inventory management, and computerized bookkeeping.',
                'duration': '2 Months',
                'fee': 8000.00
            },
            {
                'name': 'Cyber Security & Ethical Hacking',
                'description': 'Learn network security, vulnerability assessment, penetration testing fundamentals, and ethical hacking.',
                'duration': '3 Months',
                'fee': 18000.00
            }
        ]

        created_courses = []
        for cdata in courses_data:
            course, created = Course.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'description': cdata['description'],
                    'duration': cdata['duration'],
                    'fee': cdata['fee']
                }
            )
            created_courses.append(course)
            status = "Created" if created else "Already exists"
            self.stdout.write(f"Course: {course.name} ({status})")

        certificates_data = [
            {
                'certificate_id': 'CERT-2026-PY0001',
                'student_name': 'Rahul Sharma',
                'course': created_courses[0],
                'issue_date': date(2026, 2, 15),
                'grade': 'A+'
            },
            {
                'certificate_id': 'CERT-2026-FS0002',
                'student_name': 'Priya Patel',
                'course': created_courses[1],
                'issue_date': date(2026, 3, 20),
                'grade': 'A'
            },
            {
                'certificate_id': 'CERT-2026-DS0003',
                'student_name': 'Amit Verma',
                'course': created_courses[2],
                'issue_date': date(2026, 4, 10),
                'grade': 'A+'
            },
            {
                'certificate_id': 'CERT-2026-AC0004',
                'student_name': 'Sneha Gupta',
                'course': created_courses[3],
                'issue_date': date(2026, 5, 1),
                'grade': 'O (Outstanding)'
            }
        ]

        for cert_data in certificates_data:
            cert, created = Certificate.objects.get_or_create(
                certificate_id=cert_data['certificate_id'],
                defaults={
                    'student_name': cert_data['student_name'],
                    'course': cert_data['course'],
                    'issue_date': cert_data['issue_date'],
                    'grade': cert_data['grade']
                }
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"Certificate: {cert.certificate_id} for {cert.student_name} ({status})")

        from courses.models import CourseOffer
        offers_data = [
            {
                'title': '30% OFF on Python Full Stack Course',
                'badge': '🎉 LIMITED OFFER',
                'discount': '30% OFF',
                'course': created_courses[0],
                'priority': 10,
                'status': 'active'
            },
            {
                'title': 'New AI & ML Advanced Batch Starts 15 Aug',
                'badge': '🚀 NEW BATCH',
                'discount': 'Enroll Now',
                'course': created_courses[2],
                'priority': 8,
                'status': 'active'
            },
            {
                'title': 'Free Verified Certificate with Web Development Course',
                'badge': '📜 FREE CERTIFICATE',
                'discount': 'Free Certification',
                'course': created_courses[1],
                'priority': 5,
                'status': 'active'
            },
            {
                'title': 'Early Bird Special Discount on Financial Accounting',
                'badge': '⏰ LIMITED TIME',
                'discount': '20% OFF',
                'course': created_courses[3],
                'priority': 3,
                'status': 'active'
            }
        ]

        for offer_item in offers_data:
            offer, created = CourseOffer.objects.get_or_create(
                title=offer_item['title'],
                defaults={
                    'badge': offer_item['badge'],
                    'discount': offer_item['discount'],
                    'course': offer_item['course'],
                    'priority': offer_item['priority'],
                    'status': offer_item['status'],
                    'created_by': admin_user
                }
            )
            status_str = "Created" if created else "Already exists"
            self.stdout.write(f"Course Offer: {offer.title} ({status_str})")

        self.stdout.write(self.style.SUCCESS("Successfully seeded courses, certificates, and latest offers!"))
