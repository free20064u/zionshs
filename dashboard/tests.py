from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from school.models import Department, Subject
from students.models import Programme, SchoolClass, Student
from teachers.models import Responsibility, Teacher


class DashboardAdministrationStatsTests(TestCase):
    def setUp(self):
        self.admin_responsibility = Responsibility.objects.create(
            title=Responsibility.ResponsibilityTitle.ASSISTANT_HEADTEACHER_ADMINISTRATION,
            description='Administrative leadership',
        )

        assigned_student_user = CustomUser.objects.create_user(
            email='assigned.student@example.com',
            password='pass12345',
            first_name='Assigned',
            last_name='Student',
            role=CustomUser.Role.STUDENT,
        )
        Student.objects.create(
            user=assigned_student_user,
            admission_number='STD001',
            programme=Programme.SCIENCE,
            school_class_id=None,
        )

    def _create_teacher_user(self, email, role=CustomUser.Role.TEACHER):
        user = CustomUser.objects.create_user(
            email=email,
            password='pass12345',
            first_name='Alex',
            last_name='Mensah',
            role=role,
        )
        Teacher.objects.create(
            user=user,
            staff_id=f"STF{Teacher.objects.count() + 1:03d}",
            responsibility=self.admin_responsibility,
        )
        return user

    def test_teacher_with_admin_responsibility_does_not_see_unassigned_students_stat(self):
        teacher_user = self._create_teacher_user('teacher.admin@example.com')

        self.client.force_login(teacher_user)
        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Administrative Leadership')
        self.assertNotContains(response, 'Unassigned Students')
        self.assertContains(response, 'Assigned Students')

    def test_direct_admin_role_still_sees_unassigned_students_stat(self):
        admin_user = CustomUser.objects.create_user(
            email='assistant.head.admin@example.com',
            password='pass12345',
            first_name='Admin',
            last_name='Leader',
            role=CustomUser.Role.AH_ADMIN,
        )

        self.client.force_login(admin_user)
        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Administrative Leadership')
        self.assertContains(response, 'Unassigned Students')


class DashboardAcademicManagementTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Science Department')
        self.subject = Subject.objects.create(name='Physics', department=self.department)
        SchoolClass.objects.create(programme=Programme.SCIENCE, stream='A', registration_year=2026)

        self.academic_user = CustomUser.objects.create_user(
            email='academic.lead@example.com',
            password='pass12345',
            first_name='Academic',
            last_name='Lead',
            role=CustomUser.Role.AH_ACADEMIC,
        )
        self.domestic_user = CustomUser.objects.create_user(
            email='domestic.lead@example.com',
            password='pass12345',
            first_name='Domestic',
            last_name='Lead',
            role=CustomUser.Role.AH_DOMESTIC,
        )

    def test_academic_dashboard_shows_class_statistic(self):
        self.client.force_login(self.academic_user)
        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Academic Leadership')
        self.assertContains(response, 'Classes')
        self.assertContains(response, '>1<', html=False)

    def test_academic_subject_list_shows_add_and_edit_actions(self):
        self.client.force_login(self.academic_user)
        response = self.client.get(reverse('subject_list'))

        self.assertContains(response, reverse('subject_create'))
        self.assertContains(response, reverse('subject_edit', args=[self.subject.pk]))

    def test_academic_can_open_subject_create_and_edit_pages(self):
        self.client.force_login(self.academic_user)

        create_response = self.client.get(reverse('subject_create'))
        edit_response = self.client.get(reverse('subject_edit', args=[self.subject.pk]))

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(edit_response.status_code, 200)

    def test_non_academic_management_cannot_manage_subjects(self):
        self.client.force_login(self.domestic_user)

        list_response = self.client.get(reverse('subject_list'))
        create_response = self.client.get(reverse('subject_create'))
        edit_response = self.client.get(reverse('subject_edit', args=[self.subject.pk]))

        self.assertNotContains(list_response, reverse('subject_create'))
        self.assertNotContains(list_response, reverse('subject_edit', args=[self.subject.pk]))
        self.assertEqual(create_response.status_code, 302)
        self.assertEqual(edit_response.status_code, 302)
