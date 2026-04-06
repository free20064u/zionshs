import random

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import CustomUser
from school.models import Programme as CourseProgramme
from school.models import Subject
from students.models import House, Programme, SchoolClass, Student
from teachers.models import Responsibility, Teacher


class Command(BaseCommand):
    help = 'Populate the project with realistic fake school data.'

    def add_arguments(self, parser):
        parser.add_argument('--students', type=int, default=72, help='Number of students to create.')
        parser.add_argument('--teachers', type=int, default=12, help='Number of teachers to create.')
        parser.add_argument('--unassigned', type=int, default=6, help='Number of unassigned users to create.')
        parser.add_argument('--managers', type=int, default=4, help='Number of management staff accounts to create.')
        parser.add_argument('--year', type=int, default=2026, help='Registration year for generated classes.')

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()
        Faker.seed(42)
        random.seed(42)

        student_count = options['students']
        teacher_count = options['teachers']
        unassigned_count = options['unassigned']
        manager_count = options['managers']
        registration_year = options['year']

        self._ensure_houses()
        self._ensure_responsibilities()
        created_subjects, created_courses = self._ensure_subjects_and_courses(fake)

        created_students = self._create_students(fake, student_count, registration_year)
        created_teachers = self._create_teachers(fake, teacher_count)
        created_managers = self._create_management_teachers(fake, manager_count)
        created_unassigned = self._create_unassigned_users(fake, unassigned_count)

        self.stdout.write(self.style.SUCCESS('Seed completed successfully.'))
        self.stdout.write(f'Subjects ensured: {created_subjects}')
        self.stdout.write(f'Courses ensured: {created_courses}')
        self.stdout.write(f'Students created: {created_students}')
        self.stdout.write(f'Teachers created: {created_teachers}')
        self.stdout.write(f'Managers created: {created_managers}')
        self.stdout.write(f'Unassigned users created: {created_unassigned}')
        self.stdout.write(f'Total classes: {SchoolClass.objects.count()}')
        self.stdout.write(f'Total houses: {House.objects.count()}')
        self.stdout.write(f'Total courses: {CourseProgramme.objects.count()}')
        self.stdout.write(f'Total subjects: {Subject.objects.count()}')

    def _ensure_houses(self):
        for name in ['House 1', 'House 2', 'House 3', 'House 4']:
            House.objects.get_or_create(name=name, defaults={'description': ''})

    def _ensure_responsibilities(self):
        for title, _ in Responsibility.ResponsibilityTitle.choices:
            Responsibility.objects.get_or_create(title=title, defaults={'description': ''})

    def _ensure_subjects_and_courses(self, fake):
        subject_names = [
            'English Language',
            'Core Mathematics',
            'Integrated Science',
            'Social Studies',
            'Biology',
            'Chemistry',
            'Physics',
            'Economics',
            'Financial Accounting',
            'Business Management',
            'General Agriculture',
            'Crop Husbandry',
            'Food and Nutrition',
            'Management in Living',
            'Government',
            'History',
            'Literature in English',
            'Graphic Design',
            'Picture Making',
            'Sculpture',
        ]
        created_subjects = 0
        for name in subject_names:
            _, created = Subject.objects.get_or_create(name=name)
            if created:
                created_subjects += 1

        subject_map = {subject.name: subject for subject in Subject.objects.all()}
        programme_blueprints = [
            ('General Science', ['English Language', 'Core Mathematics', 'Integrated Science', 'Social Studies', 'Biology', 'Chemistry', 'Physics']),
            ('Business', ['English Language', 'Core Mathematics', 'Social Studies', 'Economics', 'Financial Accounting', 'Business Management']),
            ('Agriculture', ['English Language', 'Core Mathematics', 'Integrated Science', 'General Agriculture', 'Crop Husbandry']),
            ('Home Economics', ['English Language', 'Core Mathematics', 'Social Studies', 'Food and Nutrition', 'Management in Living']),
            ('General Arts', ['English Language', 'Core Mathematics', 'Social Studies', 'Government', 'History', 'Literature in English']),
            ('Visual Arts', ['English Language', 'Core Mathematics', 'Social Studies', 'Graphic Design', 'Picture Making', 'Sculpture']),
        ]

        created_courses = 0
        for order, (title, subject_names_for_course) in enumerate(programme_blueprints, start=1):
            course, created = CourseProgramme.objects.get_or_create(
                title=title,
                defaults={'description': fake.paragraph(nb_sentences=4), 'order': order},
            )
            if created:
                created_courses += 1
            else:
                course.order = order
                if not course.description:
                    course.description = fake.paragraph(nb_sentences=4)
                course.save(update_fields=['order', 'description'])

            course.subjects.set([subject_map[name] for name in subject_names_for_course if name in subject_map])

        return created_subjects, created_courses

    def _create_students(self, fake, count, registration_year):
        programmes = [value for value, _ in Programme.choices]
        houses = list(House.objects.all())
        created = 0
        start_index = CustomUser.objects.filter(role="Student").count()

        for index in range(count):
            email = f'student{start_index + index + 1}@wbmzionshs.test'
            if CustomUser.objects.filter(email=email).exists():
                continue

            programme = programmes[index % len(programmes)]
            stream = SchoolClass.suggest_stream(programme, registration_year)
            school_class, _ = SchoolClass.objects.get_or_create(
                programme=programme,
                stream=stream,
                registration_year=registration_year,
            )

            first_name = fake.first_name()
            last_name = fake.last_name()
            user = CustomUser.objects.create_user(
                email=email,
                password='StrongPass123!',
                first_name=first_name,
                last_name=last_name,
                gender=random.choice([choice[0] for choice in CustomUser.Gender.choices]),
                role=CustomUser.Role.STUDENT,
            )

            Student.objects.create(
                user=user,
                admission_number=f'WBM-STU-{registration_year}-{index + 1:03d}',
                programme=programme,
                house=random.choice(houses),
                school_class=school_class,
                date_of_birth=fake.date_of_birth(minimum_age=14, maximum_age=20),
                date_admitted=fake.date_between(start_date='-2y', end_date='today'),
                guardian_name=fake.name(),
                guardian_phone=fake.phone_number()[:30],
                address=fake.address(),
            )
            created += 1

        return created

    def _create_teachers(self, fake, count):
        departments = [
            'Science',
            'Business',
            'Agriculture',
            'Home Economics',
            'Visual Arts',
            'General Arts',
        ]
        specialties = [
            'Biology',
            'Chemistry',
            'Physics',
            'Economics',
            'Financial Accounting',
            'Crop Science',
            'Food and Nutrition',
            'Graphic Design',
            'History',
            'Government',
        ]
        responsibilities = list(Responsibility.objects.all())
        created = 0
        start_index = CustomUser.objects.filter(role="Teacher").count()

        for index in range(count):
            email = f'teacher{start_index + index + 1}@wbmzionshs.test'
            if CustomUser.objects.filter(email=email).exists():
                continue

            first_name = fake.first_name()
            last_name = fake.last_name()
            user = CustomUser.objects.create_user(
                email=email,
                password='StrongPass123!',
                first_name=first_name,
                last_name=last_name,
                gender=random.choice([choice[0] for choice in CustomUser.Gender.choices]),
                role=CustomUser.Role.TEACHER,
            )

            teacher = Teacher.objects.create(
                user=user,
                staff_id=f'WBM-TCH-{index + 1:03d}',
                department=random.choice(departments),
                subject_specialty=random.choice(specialties),
                date_hired=fake.date_between(start_date='-10y', end_date='today'),
                phone_number=fake.phone_number()[:30],
            )

            assigned = random.sample(responsibilities, k=random.randint(0, min(2, len(responsibilities))))
            if assigned:
                teacher.responsibilities.set(assigned)
            created += 1

        return created

    def _create_management_teachers(self, fake, count):
        management_titles = [
            Responsibility.ResponsibilityTitle.HEADTEACHER,
            Responsibility.ResponsibilityTitle.ASSISTANT_HEADTEACHER_ACADEMIC,
            Responsibility.ResponsibilityTitle.ASSISTANT_HEADTEACHER_DOMESTIC,
            Responsibility.ResponsibilityTitle.ASSISTANT_HEADTEACHER_ADMINISTRATION,
        ]
        created = 0
        start_index = CustomUser.objects.filter(email__icontains='manager').count()

        for index, title in enumerate(management_titles[:count], start=1):
            email = f'manager{start_index + index}@wbmzionshs.test'
            if CustomUser.objects.filter(email=email).exists():
                continue

            user = CustomUser.objects.create_user(
                email=email,
                password='StrongPass123!',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=random.choice([choice[0] for choice in CustomUser.Gender.choices]),
                role=CustomUser.Role.TEACHER,
            )

            teacher = Teacher.objects.create(
                user=user,
                staff_id=f'WBM-MGT-{index:03d}',
                department=random.choice([value for value, _ in Programme.choices]),
                subject_specialty=fake.random_element(elements=['Leadership', 'Academics', 'Administration', 'Pastoral Care']),
                date_hired=fake.date_between(start_date='-12y', end_date='today'),
                phone_number=fake.phone_number()[:30],
            )
            teacher.responsibilities.add(Responsibility.objects.get(title=title))
            created += 1

        return created

    def _create_unassigned_users(self, fake, count):
        created = 0
        start_index = CustomUser.objects.filter(role="").count()

        for index in range(count):
            email = f'user{start_index + index + 1}@wbmzionshs.test'
            if CustomUser.objects.filter(email=email).exists():
                continue

            CustomUser.objects.create_user(
                email=email,
                password='StrongPass123!',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=random.choice([choice[0] for choice in CustomUser.Gender.choices]),
                role='',
            )
            created += 1

        return created
