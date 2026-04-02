from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    user = request.user
    student_profile = getattr(user, 'student_profile', None)
    teacher_profile = getattr(user, 'teacher_profile', None)

    responsibilities = []
    responsibility_titles = []
    dashboard_kind = 'unassigned'

    if user.role == 'Student' and student_profile:
        dashboard_kind = 'student'
    elif user.role == 'Teacher' and teacher_profile:
        dashboard_kind = 'teacher'
        responsibilities = list(teacher_profile.responsibilities.all())
        responsibility_titles = [item.title for item in responsibilities]

    responsibility_panels = []
    panel_map = {
        'Headteacher': {
            'title': 'Headteacher Leadership',
            'summary': 'Oversee whole-school direction, performance culture, and strategic leadership.',
            'items': [
                'Monitor academic and pastoral performance across the school.',
                'Coordinate senior leadership decisions and school-wide priorities.',
                'Review staff effectiveness, student outcomes, and school culture.',
            ],
        },
        'Assistant Headteacher Academic': {
            'title': 'Academic Leadership',
            'summary': 'Support teaching quality, curriculum planning, assessment, and academic coordination.',
            'items': [
                'Track classroom quality, results trends, and departmental delivery.',
                'Coordinate schemes of learning, exams planning, and academic interventions.',
                'Support heads of department with curriculum execution and standards.',
            ],
        },
        'Assistant Headteacher Domestic': {
            'title': 'Domestic Oversight',
            'summary': 'Lead student welfare, boarding or domestic arrangements, and campus wellbeing routines.',
            'items': [
                'Coordinate student welfare and domestic supervision systems.',
                'Support pastoral discipline, house routines, and student wellbeing structures.',
                'Monitor hostel or domestic operations where applicable.',
            ],
        },
        'Assistant Headteacher Administration': {
            'title': 'Administrative Leadership',
            'summary': 'Manage operational workflows, documentation, timetables, and administrative compliance.',
            'items': [
                'Coordinate official school records, internal processes, and reporting routines.',
                'Support timetable, staffing logistics, and administrative communication flow.',
                'Maintain consistency in policy implementation and office coordination.',
            ],
        },
        'Head of Department': {
            'title': 'Department Leadership',
            'summary': 'Lead subject teams, instructional quality, and departmental planning.',
            'items': [
                f'Guide departmental work within {teacher_profile.department if teacher_profile else "your assigned department"}.',
                'Support lesson planning, moderation, and subject delivery standards.',
                'Track subject performance and coordinate departmental meetings.',
            ],
        },
        'Senior House Teacher': {
            'title': 'Senior House Leadership',
            'summary': 'Coordinate pastoral life, house order, and student welfare leadership at house level.',
            'items': [
                'Oversee house discipline, routines, and student mentoring structures.',
                'Support house teachers with welfare coordination and student follow-up.',
                'Report key house concerns to school leadership when necessary.',
            ],
        },
        'House Teacher': {
            'title': 'House Support Duties',
            'summary': 'Support daily house administration, student supervision, and pastoral care.',
            'items': [
                'Monitor student wellbeing and house conduct on a routine basis.',
                'Work with senior house leadership to maintain orderly house systems.',
                'Provide direct pastoral support and day-to-day student follow-up.',
            ],
        },
    }

    for title in responsibility_titles:
        panel = panel_map.get(title)
        if panel:
            responsibility_panels.append(panel)

    context = {
        'dashboard_kind': dashboard_kind,
        'student_profile': student_profile,
        'teacher_profile': teacher_profile,
        'responsibilities': responsibilities,
        'responsibility_titles': responsibility_titles,
        'responsibility_panels': responsibility_panels,
        'role_highlights': [
            'Your dashboard is personalized according to the role assigned by school administration.',
            'Students can quickly view programme, house, and class placement information.',
            'Teachers can track their department profile and assigned responsibilities in one place.',
        ],
    }
    return render(request, 'dashboard/index.html', context)
