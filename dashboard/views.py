from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from school.models import Programme as CourseProgramme
from school.models import Subject
from students.models import House, Programme, SchoolClass, Student
from teachers.models import Teacher


TOP_MANAGEMENT_ROLES = [
    'Headteacher',
    'Assistant Headteacher Academic',
    'Assistant Headteacher Domestic',
    'Assistant Headteacher Administration',
]


def _management_titles(user):
    titles = set()

    if getattr(user, 'role', None) in TOP_MANAGEMENT_ROLES:
        titles.add(user.role)

    teacher_profile = getattr(user, 'teacher_profile', None)
    if teacher_profile:
        titles.update(
            teacher_profile.responsibilities.values_list('title', flat=True)
        )

    return titles


def is_top_management(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or any(title in TOP_MANAGEMENT_ROLES for title in _management_titles(user))


def _page_context(title, subtitle):
    return {
        'page_title': title,
        'page_subtitle': subtitle,
    }


@login_required
def dashboard_view(request):
    user = request.user
    student_profile = getattr(user, 'student_profile', None)
    teacher_profile = getattr(user, 'teacher_profile', None)
    management_titles = _management_titles(user)

    dashboard_kind = 'unassigned'
    if user.role == 'Student' and student_profile:
        dashboard_kind = 'student'
    elif user.role == 'Teacher' and teacher_profile:
        dashboard_kind = 'teacher'

    school_stats = {
        'student_total': Student.objects.count(),
        'teacher_total': Teacher.objects.count(),
        'class_total': SchoolClass.objects.count(),
        'house_total': House.objects.count(),
        'course_total': CourseProgramme.objects.count(),
        'subject_total': Subject.objects.count(),
        'assigned_student_total': Student.objects.exclude(school_class__isnull=True).count(),
        'unassigned_student_total': Student.objects.filter(school_class__isnull=True).count(),
    }

    programme_stats = []
    for i, (programme_value, programme_label) in enumerate(Programme.choices):
        programme_stats.append(
            {
                'label': programme_label,
                'value': Student.objects.filter(programme=programme_value).count(),
                'url': f"{reverse('student_list')}?programme={programme_value}",
                'color': 'primary' if i % 2 == 0 else 'info',
                'icon': 'fa-book-open',
            }
        )

    house_stats = []
    for i, house in enumerate(House.objects.all().order_by('name')):
        house_stats.append(
            {
                'label': house.name,
                'value': house.students.count(),
                'url': f"{reverse('student_list')}?house={house.pk}",
                'color': 'warning' if i % 2 == 0 else 'success',
                'icon': 'fa-trophy',
            }
        )

    department_teacher_total = 0
    department_student_total = 0
    department_class_total = 0
    if teacher_profile and teacher_profile.department:
        department_name = teacher_profile.department
        department_teacher_total = Teacher.objects.filter(department=department_name).count()
        if department_name in dict(Programme.choices):
            department_student_total = Student.objects.filter(programme=department_name).count()
            department_class_total = SchoolClass.objects.filter(programme=department_name).count()

    panel_map = {
        'Headteacher': {
            'title': 'Headteacher Leadership',
            'stats': [
                {'label': 'Students', 'value': school_stats['student_total'], 'url': reverse('student_list'), 'icon': 'fa-graduation-cap'},
                {'label': 'Teachers', 'value': school_stats['teacher_total'], 'url': reverse('teacher_list'), 'icon': 'fa-users'},
                {'label': 'Classes', 'value': school_stats['class_total'], 'url': reverse('class_list'), 'icon': 'fa-book-open'},
                {'label': 'Houses', 'value': school_stats['house_total'], 'url': reverse('house_list'), 'icon': 'fa-trophy'},
                {'label': 'Courses', 'value': school_stats['course_total'], 'url': reverse('course_list'), 'icon': 'fa-book-open'},
                {'label': 'Subjects', 'value': school_stats['subject_total'], 'url': reverse('subject_list'), 'icon': 'fa-star'},
            ],
        },
        'Assistant Headteacher Academic': {
            'title': 'Academic Leadership',
            'stats': programme_stats + [
                {'label': 'Courses', 'value': school_stats['course_total'], 'url': reverse('course_list'), 'icon': 'fa-book-open'},
                {'label': 'Subjects', 'value': school_stats['subject_total'], 'url': reverse('subject_list'), 'icon': 'fa-star'},
            ],
        },
        'Assistant Headteacher Domestic': {
            'title': 'Domestic Oversight',
            'stats': house_stats,
        },
        'Assistant Headteacher Administration': {
            'title': 'Administrative Leadership',
            'stats': [
                {'label': 'Assigned Students', 'value': school_stats['assigned_student_total'], 'url': f"{reverse('student_list')}?assignment=assigned", 'icon': 'fa-users'},
                {'label': 'Unassigned Students', 'value': school_stats['unassigned_student_total'], 'url': f"{reverse('student_list')}?assignment=unassigned", 'icon': 'fa-users'},
                {'label': 'Teacher Accounts', 'value': school_stats['teacher_total'], 'url': reverse('teacher_list'), 'icon': 'fa-users'},
                {'label': 'School Classes', 'value': school_stats['class_total'], 'url': reverse('class_list'), 'icon': 'fa-book-open'},
                {'label': 'Courses', 'value': school_stats['course_total'], 'url': reverse('course_list'), 'icon': 'fa-book-open'},
                {'label': 'Subjects', 'value': school_stats['subject_total'], 'url': reverse('subject_list'), 'icon': 'fa-star'},
            ],
        },
        'Head of Department': {
            'title': 'Department Leadership',
            'stats': [
                {
                    'label': 'Department Teachers',
                    'value': department_teacher_total,
                    'url': f"{reverse('teacher_list')}?department={teacher_profile.department}" if teacher_profile and teacher_profile.department else '',
                    'icon': 'fa-users',
                },
                {
                    'label': 'Programme Students',
                    'value': department_student_total,
                    'url': f"{reverse('student_list')}?programme={teacher_profile.department}" if teacher_profile and teacher_profile.department in dict(Programme.choices) else '',
                    'icon': 'fa-graduation-cap',
                },
                {
                    'label': 'Programme Classes',
                    'value': department_class_total,
                    'url': f"{reverse('class_list')}?programme={teacher_profile.department}" if teacher_profile and teacher_profile.department in dict(Programme.choices) else '',
                    'icon': 'fa-book-open',
                },
                {'label': 'Total Subjects', 'value': school_stats['subject_total'], 'url': reverse('subject_list'), 'icon': 'fa-star'},
            ],
        },
    }

    responsibility_panels = []
    if is_top_management(user):
        for title in TOP_MANAGEMENT_ROLES:
            if title in management_titles and title in panel_map:
                responsibility_panels.append(panel_map[title])

    display_school_stats = [
        {'label': 'Total Students', 'value': school_stats['student_total'], 'icon': 'fa-graduation-cap', 'url': reverse('student_list')},
        {'label': 'Total Teachers', 'value': school_stats['teacher_total'], 'icon': 'fa-users', 'url': reverse('teacher_list')},
        {'label': 'Total Classes', 'value': school_stats['class_total'], 'icon': 'fa-book-open', 'url': reverse('class_list')},
        {'label': 'Total Houses', 'value': school_stats['house_total'], 'icon': 'fa-trophy', 'url': reverse('house_list')},
        {'label': 'Total Courses', 'value': school_stats['course_total'], 'icon': 'fa-book-open', 'url': reverse('course_list')},
        {'label': 'Total Subjects', 'value': school_stats['subject_total'], 'icon': 'fa-star', 'url': reverse('subject_list')},
    ]

    context = {
        'dashboard_kind': dashboard_kind,
        'student_profile': student_profile,
        'teacher_profile': teacher_profile,
        'responsibility_panels': responsibility_panels,
        'display_school_stats': display_school_stats,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
@user_passes_test(is_top_management)
def student_list(request):
    students = Student.objects.select_related('user', 'house', 'school_class').order_by('admission_number')
    q = request.GET.get('q', '').strip()
    programme = request.GET.get('programme', '')
    house_id = request.GET.get('house', '')
    assignment = request.GET.get('assignment', '')

    if q:
        students = students.filter(user__first_name__icontains=q)
    if programme:
        students = students.filter(programme=programme)
    if house_id:
        students = students.filter(house_id=house_id)
    if assignment == 'assigned':
        students = students.exclude(school_class__isnull=True)
    elif assignment == 'unassigned':
        students = students.filter(school_class__isnull=True)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    context = {
        'students': students,
        'q': q,
        'programme': programme,
        'assignment': assignment,
        'house_id': house_id,
        'all_houses': House.objects.all().order_by('name'),
        'all_programmes': Programme.choices,
        **_page_context('Students', 'Manager access to student records from the dashboard.'),
    }
    return render(request, 'dashboard/student_list.html', context)


@login_required
@user_passes_test(is_top_management)
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').prefetch_related('responsibilities').order_by('staff_id')
    department = request.GET.get('department')
    if department:
        teachers = teachers.filter(department=department)

    paginator = Paginator(teachers, 10)
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)

    context = {
        'teachers': teachers,
        'department': department,
        **_page_context('Teachers', 'Manager access to teaching and leadership staff records.'),
    }
    return render(request, 'dashboard/teacher_list.html', context)


@login_required
@user_passes_test(is_top_management)
def class_list(request):
    classes = SchoolClass.objects.prefetch_related('students').order_by('registration_year', 'programme', 'stream')
    programme = request.GET.get('programme')
    if programme:
        classes = classes.filter(programme=programme)

    paginator = Paginator(classes, 10)
    page_number = request.GET.get('page')
    classes = paginator.get_page(page_number)

    context = {
        'classes': classes,
        'programme': programme,
        **_page_context('Classes', 'Manager access to school classes and enrolment counts.'),
    }
    return render(request, 'dashboard/class_list.html', context)


@login_required
@user_passes_test(is_top_management)
def house_list(request):
    houses = House.objects.all().order_by('name')
    paginator = Paginator(houses, 10)
    page_number = request.GET.get('page')
    houses = paginator.get_page(page_number)

    context = {
        'houses': houses,
        **_page_context('Houses', 'Manager access to all school houses and their student totals.'),
    }
    return render(request, 'dashboard/house_list.html', context)


@login_required
@user_passes_test(is_top_management)
def course_list(request):
    courses = CourseProgramme.objects.prefetch_related('subjects').order_by('order', 'title')
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)

    context = {
        'courses': courses,
        **_page_context('Courses', 'Manager access to academic programmes and linked subjects.'),
    }
    return render(request, 'dashboard/course_list.html', context)


@login_required
@user_passes_test(is_top_management)
def subject_list(request):
    subjects = Subject.objects.all().order_by('name')
    paginator = Paginator(subjects, 10)
    page_number = request.GET.get('page')
    subjects = paginator.get_page(page_number)

    context = {
        'subjects': subjects,
        **_page_context('Subjects', 'Manager access to curriculum subjects from the dashboard.'),
    }
    return render(request, 'dashboard/subject_list.html', context)


@login_required
@user_passes_test(is_top_management)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'dashboard/student_detail.html', {'student': student})


@login_required
@user_passes_test(is_top_management)
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'dashboard/teacher_detail.html', {'teacher': teacher})


@login_required
@user_passes_test(is_top_management)
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'dashboard/subject_detail.html', {'subject': subject})


@login_required
@user_passes_test(is_top_management)
def course_detail(request, pk):
    course = get_object_or_404(CourseProgramme, pk=pk)
    return render(request, 'dashboard/course_detail.html', {'course': course})


@login_required
@user_passes_test(is_top_management)
def house_detail(request, pk):
    house = get_object_or_404(House, pk=pk)
    return render(request, 'dashboard/house_detail.html', {'house': house})
