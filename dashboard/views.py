from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from school.forms import ProgrammeForm, DepartmentForm
from school.models import Programme as CourseProgramme, Department
from school.models import Subject
from students.forms import HouseForm, StudentAdminForm, SchoolClassForm
from students.models import House, Programme, SchoolClass, Student
from teachers.forms import ResponsibilityForm, TeacherAdminForm
from teachers.models import Responsibility
from teachers.models import Teacher


TOP_MANAGEMENT_ROLES = [
    'Headteacher',
    'Assistant Headteacher Academic',
    'Assistant Headteacher Domestic',
    'Assistant Headteacher Administration',
]
TEACHER_MANAGEMENT_ROLES = [
    'Headteacher',
    'Assistant Headteacher Administration',
]
CLASS_MANAGEMENT_ROLES = [
    'Headteacher',
    'Assistant Headteacher Academic',
    'Assistant Headteacher Administration',
]
HOUSE_MANAGEMENT_ROLES = [
    'Headteacher',
    'Assistant Headteacher Administration',
    'Assistant Headteacher Domestic',
]
FORM_TEACHER_ROLE = Responsibility.ResponsibilityTitle.FORM_TEACHER


def _management_titles(user):
    titles = set()

    if getattr(user, 'role', None) in TOP_MANAGEMENT_ROLES:
        titles.add(user.role)

    teacher_profile = getattr(user, 'teacher_profile', None)
    if teacher_profile and teacher_profile.responsibility:
        titles.add(teacher_profile.responsibility.title)

    return titles


def is_top_management(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or any(title in TOP_MANAGEMENT_ROLES for title in _management_titles(user))


def can_manage_teachers(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or any(title in TEACHER_MANAGEMENT_ROLES for title in _management_titles(user))


def can_manage_classes(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or any(title in CLASS_MANAGEMENT_ROLES for title in _management_titles(user))


def can_manage_houses(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or any(title in HOUSE_MANAGEMENT_ROLES for title in _management_titles(user))


def is_form_teacher(user):
    if not user.is_authenticated:
        return False
    return FORM_TEACHER_ROLE in _management_titles(user)


def can_access_class_records(user):
    return is_top_management(user) or is_form_teacher(user)


def _assigned_form_classes(user):
    teacher_profile = getattr(user, 'teacher_profile', None)
    if not teacher_profile:
        return SchoolClass.objects.none()
    return SchoolClass.objects.filter(form_teacher=teacher_profile)


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
        'department_total': Department.objects.count(),
        'responsibility_total': Responsibility.objects.count(),
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
        department_name = teacher_profile.department.name
        department_teacher_total = Teacher.objects.filter(department=teacher_profile.department).count()
        if department_name in dict(Programme.choices):
            department_student_total = Student.objects.filter(programme=department_name).count()
            department_class_total = SchoolClass.objects.filter(programme=department_name).count()
    assigned_form_classes = SchoolClass.objects.none()
    if teacher_profile:
        assigned_form_classes = (
            SchoolClass.objects.filter(form_teacher=teacher_profile)
            .prefetch_related('students')
            .order_by('registration_year', 'programme', 'stream')
        )

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
                {'label': 'Departments', 'value': school_stats['department_total'], 'url': reverse('department_list'), 'icon': 'fa-building'},
                {'label': 'Responsibilities', 'value': school_stats['responsibility_total'], 'url': reverse('responsibility_list'), 'icon': 'fa-shield-check'},
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
                {'label': 'Departments', 'value': school_stats['department_total'], 'url': reverse('department_list'), 'icon': 'fa-building'},
                {'label': 'Responsibilities', 'value': school_stats['responsibility_total'], 'url': reverse('responsibility_list'), 'icon': 'fa-shield-check'},
            ],
        },
        'Head of Department': {
            'title': 'Department Leadership',
            'stats': [
                {
                    'label': 'Department Teachers',
                    'value': department_teacher_total,
                    'url': f"{reverse('teacher_list')}?department={teacher_profile.department.pk}" if teacher_profile and teacher_profile.department else '',
                    'icon': 'fa-users',
                },
                {
                    'label': 'Programme Students',
                    'value': department_student_total,
                    'url': f"{reverse('student_list')}?programme={teacher_profile.department.name}" if teacher_profile and department_name in dict(Programme.choices) else '',
                    'icon': 'fa-graduation-cap',
                },
                {
                    'label': 'Programme Classes',
                    'value': department_class_total,
                    'url': f"{reverse('class_list')}?programme={teacher_profile.department.name}" if teacher_profile and department_name in dict(Programme.choices) else '',
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
        {'label': 'Total Departments', 'value': school_stats['department_total'], 'icon': 'fa-building', 'url': reverse('department_list')},
    ]
    if is_top_management(user):
        display_school_stats.append(
            {'label': 'Responsibilities', 'value': school_stats['responsibility_total'], 'icon': 'fa-shield-check', 'url': reverse('responsibility_list')}
        )

    context = {
        'dashboard_kind': dashboard_kind,
        'student_profile': student_profile,
        'teacher_profile': teacher_profile,
        'responsibility_panels': responsibility_panels,
        'display_school_stats': display_school_stats,
        'assigned_form_classes': assigned_form_classes,
        'is_form_teacher': is_form_teacher(user),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
@user_passes_test(can_access_class_records)
def student_list(request):
    students = Student.objects.select_related('user', 'house', 'school_class').order_by('admission_number')
    q = request.GET.get('q', '').strip()
    programme = request.GET.get('programme', '')
    house_id = request.GET.get('house', '')
    assignment = request.GET.get('assignment', '')
    school_class_id = request.GET.get('school_class', '')

    if not is_top_management(request.user):
        assigned_classes = _assigned_form_classes(request.user)
        students = students.filter(school_class__in=assigned_classes)

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
    if school_class_id:
        students = students.filter(school_class_id=school_class_id)

    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)

    selected_class = None
    if school_class_id:
        visible_classes = _assigned_form_classes(request.user) if not is_top_management(request.user) else SchoolClass.objects.all()
        selected_class = visible_classes.filter(pk=school_class_id).first()

    context = {
        'students': students,
        'q': q,
        'programme': programme,
        'assignment': assignment,
        'house_id': house_id,
        'school_class_id': school_class_id,
        'selected_class': selected_class,
        'all_houses': House.objects.all().order_by('name'),
        'all_programmes': Programme.choices,
        **_page_context(
            'Students',
            'Manager access to student records from the dashboard.'
            if is_top_management(request.user)
            else 'Students in your assigned form class.',
        ),
    }
    return render(request, 'dashboard/student_list.html', context)


@login_required
@user_passes_test(is_top_management)
def teacher_list(request):
    teachers = Teacher.objects.select_related('user', 'responsibility').order_by('staff_id')

    q = request.GET.get('q', '').strip()
    department = request.GET.get('department', '')
    specialty = request.GET.get('specialty', '')

    if q:
        teachers = teachers.filter(user__first_name__icontains=q)
    if department:
        try:
            teachers = teachers.filter(department_id=department)
        except (ValueError, TypeError):
            pass
    if specialty:
        teachers = teachers.filter(subject_specialty=specialty)

    # Dynamically fetch existing values for filters
    all_departments = Department.objects.all()
    all_specialties = Teacher.objects.exclude(subject_specialty__in=['', None]).values_list('subject_specialty', flat=True).distinct().order_by('subject_specialty')

    paginator = Paginator(teachers, 10)
    page_number = request.GET.get('page')
    teachers = paginator.get_page(page_number)

    context = {
        'teachers': teachers,
        'q': q,
        'department': department,
        'specialty': specialty,
        'all_departments': all_departments,
        'all_specialties': all_specialties,
        'can_manage_teachers': can_manage_teachers(request.user),
        **_page_context('Teachers', 'Manager access to teaching and leadership staff records.'),
    }
    return render(request, 'dashboard/teacher_list.html', context)


@login_required
@user_passes_test(can_manage_teachers)
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherAdminForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher account created for {teacher.user.get_full_name()}.')
            return redirect('teacher_detail', pk=teacher.pk)
    else:
        form = TeacherAdminForm()

    return render(
        request,
        'dashboard/teacher_edit.html',
        {
            'form': form,
            'page_heading': 'Add Teacher',
            'page_description': 'Create a new teacher account, assign responsibilities, and capture staff details.',
            'submit_label': 'Create Teacher',
        },
    )


@login_required
@user_passes_test(can_access_class_records)
def class_list(request):
    classes = SchoolClass.objects.select_related('form_teacher__user').prefetch_related('students').order_by('registration_year', 'programme', 'stream')
    programme = request.GET.get('programme')

    if not is_top_management(request.user):
        classes = classes.filter(form_teacher=getattr(request.user, 'teacher_profile', None))
    if programme:
        classes = classes.filter(programme=programme)

    paginator = Paginator(classes, 10)
    page_number = request.GET.get('page')
    classes = paginator.get_page(page_number)

    context = {
        'classes': classes,
        'programme': programme,
        'can_manage_classes': can_manage_classes(request.user),
        **_page_context(
            'Classes',
            'Manager access to school classes and enrolment counts.'
            if is_top_management(request.user)
            else 'Classes assigned to you as a form teacher.',
        ),
    }
    return render(request, 'dashboard/class_list.html', context)


@login_required
@user_passes_test(can_manage_classes)
def class_create(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            messages.success(request, f'Class {school_class.name} created successfully.')
            return redirect('class_list')
    else:
        form = SchoolClassForm()

    return render(
        request,
        'dashboard/class_form.html',
        {
            'form': form,
            'page_heading': 'Add Class',
            'page_description': 'Create a new class by selecting programme, stream and registration year.',
            'submit_label': 'Create Class',
        },
    )


@login_required
@user_passes_test(can_manage_classes)
def class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)

    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            school_class = form.save()
            messages.success(request, f'Class {school_class.name} updated successfully.')
            return redirect('class_list')
    else:
        form = SchoolClassForm(instance=school_class)

    return render(
        request,
        'dashboard/class_form.html',
        {
            'form': form,
            'school_class': school_class,
            'page_heading': f'Edit Class: {school_class.name}',
            'page_description': 'Update class details including form teacher assignment.',
            'submit_label': 'Save Changes',
        },
    )


@login_required
@user_passes_test(is_top_management)
def house_list(request):
    houses = House.objects.all().order_by('name')
    paginator = Paginator(houses, 10)
    page_number = request.GET.get('page')
    houses = paginator.get_page(page_number)

    context = {
        'houses': houses,
        'can_manage_houses': can_manage_houses(request.user),
        **_page_context('Houses', 'Manager access to all school houses and their student totals.'),
    }
    return render(request, 'dashboard/house_list.html', context)


@login_required
@user_passes_test(can_manage_houses)
def house_create(request):
    if request.method == 'POST':
        form = HouseForm(request.POST)
        if form.is_valid():
            house = form.save()
            messages.success(request, f'{house.name} house created successfully.')
            return redirect('house_detail', pk=house.pk)
    else:
        form = HouseForm()

    return render(
        request,
        'dashboard/house_form.html',
        {
            'form': form,
            'page_heading': 'Add House',
            'page_description': 'Create a new school house and set its identifying color.',
            'submit_label': 'Create House',
        },
    )


@login_required
@user_passes_test(can_manage_houses)
def house_edit(request, pk):
    house = get_object_or_404(House, pk=pk)

    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            house = form.save()
            messages.success(request, f'{house.name} house updated successfully.')
            return redirect('house_detail', pk=house.pk)
    else:
        form = HouseForm(instance=house)

    return render(
        request,
        'dashboard/house_form.html',
        {
            'form': form,
            'house': house,
            'page_heading': f'Edit {house.name}',
            'page_description': 'Update house details, color, and description.',
            'submit_label': 'Save Changes',
        },
    )


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
def course_create(request):
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'{course.title} created successfully.')
            return redirect('course_detail', pk=course.pk)
    else:
        form = ProgrammeForm()

    return render(
        request,
        'dashboard/course_form.html',
        {
            'form': form,
            'page_heading': 'Add Course',
            'page_description': 'Create a new course and link the subjects it should include.',
            'submit_label': 'Create Course',
        },
    )


@login_required
@user_passes_test(is_top_management)
def course_edit(request, pk):
    course = get_object_or_404(CourseProgramme, pk=pk)

    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'{course.title} updated successfully.')
            return redirect('course_detail', pk=course.pk)
    else:
        form = ProgrammeForm(instance=course)

    return render(
        request,
        'dashboard/course_form.html',
        {
            'form': form,
            'course': course,
            'page_heading': f'Edit {course.title}',
            'page_description': 'Update course details, subject links, and display order.',
            'submit_label': 'Save Changes',
        },
    )


@login_required
@user_passes_test(is_top_management)
def subject_list(request):
    subjects = Subject.objects.select_related('department').all().order_by('name')
    
    q = request.GET.get('q', '').strip()
    department_id = request.GET.get('department', '')

    if q:
        subjects = subjects.filter(name__icontains=q)
    if department_id:
        try:
            subjects = subjects.filter(department_id=department_id)
        except (ValueError, TypeError):
            pass

    all_departments = Department.objects.all()

    paginator = Paginator(subjects, 10)
    page_number = request.GET.get('page')
    subjects = paginator.get_page(page_number)

    context = {
        'subjects': subjects,
        'q': q,
        'department_id': department_id,
        'all_departments': all_departments,
        **_page_context('Subjects', 'Manager access to curriculum subjects from the dashboard.'),
    }
    return render(request, 'dashboard/subject_list.html', context)


@login_required
@user_passes_test(is_top_management)
def responsibility_list(request):
    responsibilities = Responsibility.objects.prefetch_related('teachers').order_by('title')
    paginator = Paginator(responsibilities, 10)
    page_number = request.GET.get('page')
    responsibilities = paginator.get_page(page_number)

    context = {
        'responsibilities': responsibilities,
        **_page_context('Responsibilities', 'Manager access to school leadership and operational responsibilities.'),
    }
    return render(request, 'dashboard/responsibility_list.html', context)


@login_required
@user_passes_test(is_top_management)
def responsibility_create(request):
    if request.method == 'POST':
        form = ResponsibilityForm(request.POST)
        if form.is_valid():
            responsibility = form.save()
            messages.success(request, f'{responsibility.title} created successfully.')
            return redirect('responsibility_list')
    else:
        form = ResponsibilityForm()

    return render(
        request,
        'dashboard/responsibility_form.html',
        {
            'form': form,
            'page_heading': 'Add Responsibility',
            'page_description': 'Create a new responsibility that can be assigned to teachers.',
            'submit_label': 'Create Responsibility',
        },
    )


@login_required
@user_passes_test(is_top_management)
def responsibility_edit(request, pk):
    responsibility = get_object_or_404(Responsibility, pk=pk)

    if request.method == 'POST':
        form = ResponsibilityForm(request.POST, instance=responsibility)
        if form.is_valid():
            responsibility = form.save()
            messages.success(request, f'{responsibility.title} updated successfully.')
            return redirect('responsibility_list')
    else:
        form = ResponsibilityForm(instance=responsibility)

    return render(
        request,
        'dashboard/responsibility_form.html',
        {
            'form': form,
            'responsibility': responsibility,
            'page_heading': f'Edit {responsibility.title}',
            'page_description': 'Update a responsibility used for teacher assignments and leadership roles.',
            'submit_label': 'Save Changes',
        },
    )


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    allowed = is_top_management(request.user)
    teacher_profile = getattr(request.user, 'teacher_profile', None)
    if not allowed and is_form_teacher(request.user) and teacher_profile:
        allowed = student.school_class_id is not None and student.school_class.form_teacher_id == teacher_profile.pk
    if not allowed:
        return redirect('dashboard')
    return render(
        request,
        'dashboard/student_detail.html',
        {
            'student': student,
            'can_edit_student': is_top_management(request.user),
        },
    )


@login_required
@user_passes_test(is_top_management)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentAdminForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details updated successfully.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentAdminForm(instance=student)

    return render(
        request,
        'dashboard/student_edit.html',
        {
            'student': student,
            'form': form,
        },
    )


@login_required
@user_passes_test(is_top_management)
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(
        request,
        'dashboard/teacher_detail.html',
        {
            'teacher': teacher,
            'can_manage_teachers': can_manage_teachers(request.user),
        },
    )


@login_required
@user_passes_test(can_manage_teachers)
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        form = TeacherAdminForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher details updated successfully.')
            return redirect('teacher_detail', pk=teacher.pk)
    else:
        form = TeacherAdminForm(instance=teacher)

    return render(
        request,
        'dashboard/teacher_edit.html',
        {
            'teacher': teacher,
            'form': form,
        },
    )


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
    return render(
        request,
        'dashboard/house_detail.html',
        {
            'house': house,
            'can_manage_houses': can_manage_houses(request.user),
        },
    )


@login_required
@user_passes_test(is_top_management)
def department_list(request):
    departments = Department.objects.all().order_by('name')
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    departments = paginator.get_page(page_number)

    context = {
        'departments': departments,
        **_page_context('Departments', 'Manager access to school departments and linked subjects.'),
    }
    return render(request, 'dashboard/department_list.html', context)


@login_required
@user_passes_test(is_top_management)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'{department.name} created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()

    return render(
        request,
        'dashboard/department_form.html',
        {
            'form': form,
            'page_heading': 'Add Department',
            'page_description': 'Create a new department that connects subjects and teachers.',
            'submit_label': 'Create Department',
        },
    )


@login_required
@user_passes_test(is_top_management)
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'{department.name} updated successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)

    return render(
        request,
        'dashboard/department_form.html',
        {
            'form': form,
            'department': department,
            'page_heading': f'Edit {department.name}',
            'page_description': 'Update department details and description.',
            'submit_label': 'Save Changes',
        },
    )
