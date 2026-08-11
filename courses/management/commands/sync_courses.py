from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Syncs all course categories and sub-courses into the Django database for Admin Panel access'

    def handle(self, *args, **options):
        self.stdout.write("Starting course database synchronization...")

        COURSES_DATA = [
            # CATEGORY 1: BASIC
            {
                "category": "Basic",
                "duration": "Basic Skills",
                "sub_courses": [
                    ("CCC", "Course on Computer Concepts certified foundation module."),
                    ("MS Office", "Microsoft Word, Excel, PowerPoint, and Outlook essentials."),
                    ("Adv. Excel", "Advanced functions, pivot tables, data visualization, and formulas."),
                    ("Adv. MSOffice", "Advanced office productivity suite, macros, and document automation."),
                    ("DEO", "Data Entry Operator skill training & typing accuracy."),
                    ("CPT", "Computer Proficiency Test preparation and core practicals."),
                    ("DTP", "Desktop Publishing fundamentals for layout, typesetting, and print."),
                    ("CAD", "Computer-Aided Design fundamentals for technical drawings.")
                ]
            },
            # CATEGORY 2: ACCOUNTING
            {
                "category": "Accounting",
                "duration": "Specialized",
                "sub_courses": [
                    ("Tally Prime Basic", "Fundamental accounting principles, vouchers, ledger, and inventory in Tally."),
                    ("Tally Prime Specialist", "Intermediate Tally Prime with GST taxation, payroll, and banking features."),
                    ("Tally Prime Xpert", "Advanced Tally Prime master module including MIS reporting and audit features.")
                ]
            },
            # CATEGORY 3: PROGRAMMING
            {
                "category": "Programming",
                "duration": "Modular Tracks",
                "sub_courses": [
                    ("C", "Procedural programming logic, memory structures, and algorithms."),
                    ("C++", "Object-oriented concepts, STL containers, and low-level development."),
                    ("C#", "Object-oriented C# development for desktop and enterprise apps."),
                    ("Python", "Python scripting, data structures, functional code, and backend concepts."),
                    ("JAVA", "Core Java OOPs, multithreading, collections framework, and JVM memory."),
                    ("PHP", "Server-side web scripting, dynamic database integration, and backend."),
                    (".NET", "Microsoft .NET application architecture and enterprise services."),
                    ("HTML", "HTML5 semantic markup, page architecture, and web standards."),
                    ("CSS", "CSS3 styling, Flexbox, Grid, animations, and responsive layout design."),
                    ("JavaScript", "Modern ES6+ JavaScript syntax, asynchronous JS, and DOM API."),
                    ("React", "Frontend React library, functional components, hooks, and state management."),
                    ("React Native", "Cross-platform mobile application development for Android & iOS."),
                    ("Flutter", "Google Flutter framework and Dart programming for cross-platform apps."),
                    ("MySQL", "Relational SQL database queries, joins, indexes, and database design.")
                ]
            },
            # CATEGORY 4: DIPLOMA (6 MONTHS)
            {
                "category": "Diploma (6 Months)",
                "duration": "6 Months",
                "sub_courses": [
                    ("Diploma in Office Automation", "6-Month diploma program in office automation tools and workflows."),
                    ("Diploma in Financial Accounting", "6-Month diploma in computerized accounting and financial management."),
                    ("Diploma in Office Automation & Financial Accounting", "6-Month dual diploma in office software and accounting."),
                    ("Diploma in Computer Programming", "6-Month diploma covering programming fundamentals and algorithms."),
                    ("Diploma in Computer Applications", "6-Month diploma in general computer applications and IT skills."),
                    ("Diploma in Graphics Design", "6-Month diploma in visual graphics, typography, and image editing."),
                    ("Diploma in Web Design", "6-Month diploma in web design, UI layouts, HTML, and CSS."),
                    ("Diploma in Graphics and Web Design", "6-Month comprehensive graphics and web design program."),
                    ("Diploma in Frontend Development", "6-Month diploma in frontend web engineering and JavaScript."),
                    ("Diploma in JAVA", "6-Month diploma in Java software development."),
                    ("Diploma in Web Development", "6-Month diploma in full-stack web development."),
                    ("Diploma in DOT Technologies", "6-Month diploma in Microsoft .NET technologies."),
                    ("Diploma in Digital Marketing", "6-Month diploma in SEO, social media, and digital marketing."),
                    ("Diploma in Data Analysis", "6-Month diploma in data analysis, Excel, SQL, and PowerBI."),
                    ("Diploma in CAD - Civil Drawing", "6-Month diploma in CAD drafting for civil engineering."),
                    ("Diploma in CAD - Mechanical Drawing", "6-Month diploma in CAD drafting for mechanical engineering."),
                    ("Diploma in 2D and 3D Drawing", "6-Month diploma in 2D and 3D technical drawing."),
                    ("Diploma in Communication Skill", "6-Month diploma in professional communication and soft skills."),
                    ("DIPLOMA in Python for Data Analysis", "6-Month diploma in Python, Pandas, and data analytics."),
                    ("DIPLOMA in Using Artificial Intelligence (AI) Tools", "6-Month diploma in AI productivity tools and workflows.")
                ]
            },
            # CATEGORY 5: ADVANCE DIPLOMA (12 MONTHS)
            {
                "category": "Advance Diploma (12 Months)",
                "duration": "12 Months",
                "sub_courses": [
                    ("Adv. Diploma in Office Automation", "12-Month advance diploma program in office automation."),
                    ("Adv. Diploma in Financial Accounting", "12-Month advance diploma in accounting and financial systems."),
                    ("Adv. Diploma in Office Automation & Financial Accounting", "12-Month dual advance diploma."),
                    ("Adv. Diploma in Computer Programming", "12-Month advance diploma in software programming."),
                    ("Adv. Diploma in Computer Applications", "12-Month advance diploma in computer applications."),
                    ("Adv. Diploma in Graphics Design", "12-Month advance diploma in graphic design & digital art."),
                    ("Adv. Diploma in Web Design", "12-Month advance diploma in modern web design."),
                    ("Adv. Diploma in Graphics and Web Design", "12-Month master diploma in graphics & web design."),
                    ("Adv. Diploma in Frontend Development", "12-Month advance diploma in frontend engineering."),
                    ("Adv. Diploma in JAVA", "12-Month advance diploma in Java software engineering."),
                    ("Adv. Diploma in Web Development", "12-Month advance diploma in web software development."),
                    ("Adv. Diploma in DOT Technologies", "12-Month advance diploma in .NET enterprise tech."),
                    ("Adv. Diploma in Digital Marketing", "12-Month advance diploma in digital marketing & analytics."),
                    ("Adv. Diploma in Data Analysis", "12-Month advance diploma in data science & analytics."),
                    ("Adv. Diploma in CAD - Civil Drawing", "12-Month advance diploma in civil CAD drafting."),
                    ("Adv. Diploma in CAD - Mechanical Drawing", "12-Month advance diploma in mechanical CAD drafting."),
                    ("Adv. Diploma in 2D and 3D Drawing", "12-Month advance diploma in 2D & 3D CAD modeling.")
                ]
            },
            # CATEGORY 6: FRONTEND / FULL STACK DEVELOPMENT
            {
                "category": "Frontend / Full Stack Development",
                "duration": "Career Track",
                "sub_courses": [
                    ("Frontend Development with React", "Specialized track in modern React frontend development."),
                    ("Full Stack Development with Python + Django", "Full stack web development track using Python & Django framework."),
                    ("Full Stack Development with PHP + Laravel", "Full stack web development track using PHP & Laravel framework."),
                    ("Full Stack Development with Angular + .Net Core", "Full stack enterprise development with Angular & .NET Core."),
                    ("MERN Stack Development", "Full stack JavaScript track using MongoDB, Express, React, & Node."),
                    ("Cross Platform App Development with React Native", "Mobile app development track using React Native."),
                    ("Cross Platform App Development with Flutter", "Mobile app development track using Flutter & Dart."),
                    ("UI/UX Design with Figma", "UI/UX design track using Figma, wireframing, & prototyping.")
                ]
            },
            # CATEGORY 7: MODULAR COURSES
            {
                "category": "Modular Courses",
                "duration": "Flexible",
                "sub_courses": [
                    ("PageMaker", "Modular course on Adobe PageMaker document layout."),
                    ("Photoshop", "Modular course on Adobe Photoshop image editing."),
                    ("CorelDraw", "Modular course on CorelDraw vector design."),
                    ("Illustrator", "Modular course on Adobe Illustrator graphics."),
                    ("InDesign", "Modular course on Adobe InDesign publishing layout."),
                    ("Canva", "Modular course on Canva digital design & templates."),
                    ("PowerBI", "Modular course on Microsoft PowerBI data visualization."),
                    ("Core JAVA", "Modular course on Core Java programming."),
                    ("Adv. JAVA", "Modular course on Advanced Java & enterprise frameworks."),
                    ("WordPress", "Modular course on WordPress CMS site building."),
                    ("Figma", "Modular course on Figma UI design."),
                    ("Bootstrap", "Modular course on Bootstrap responsive framework.")
                ]
            }
        ]

        total_created = 0
        total_updated = 0

        for cat_data in COURSES_DATA:
            cat_name = cat_data["category"]
            duration = cat_data["duration"]

            # Also create/update main category entry in Course model
            cat_obj, created = Course.objects.get_or_create(
                name=cat_name,
                defaults={
                    "description": f"Main course category for {cat_name}.",
                    "duration": duration,
                    "is_featured": True
                }
            )
            if created:
                total_created += 1
            else:
                cat_obj.duration = duration
                cat_obj.save()
                total_updated += 1

            # Create/update sub-courses in Course model
            for sub_title, sub_desc in cat_data["sub_courses"]:
                sub_obj, sub_created = Course.objects.get_or_create(
                    name=sub_title,
                    defaults={
                        "description": sub_desc,
                        "duration": duration,
                        "is_featured": False
                    }
                )
                if sub_created:
                    total_created += 1
                else:
                    sub_obj.description = sub_desc
                    sub_obj.duration = duration
                    sub_obj.save()
                    total_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully synced courses to Admin database! Created: {total_created}, Updated: {total_updated}."
        ))
