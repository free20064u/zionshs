from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import Facility, NewsItem, Programme

FEATURES = [
    {
        'title': 'Experienced Faculty',
        'description': 'Qualified educators blend structure, mentorship, and modern teaching practice in every classroom.',
    },
    {
        'title': 'STEM and Innovation',
        'description': 'Students learn through robotics clubs, science labs, coding sessions, and project-based collaboration.',
    },
    {
        'title': 'Character Formation',
        'description': 'We cultivate discipline, empathy, service, and confidence alongside academic achievement.',
    },
]

STATS = [
    {'value': '98%', 'label': 'Exam pass rate'},
    {'value': '24', 'label': 'Clubs and societies'},
    {'value': '16:1', 'label': 'Student-teacher ratio'},
    {'value': '12', 'label': 'Years of trusted service'},
]

ADMISSION_STEPS = [
    'Check your placement on the CSSPS portal (www.cssps.gov.gh) using your Index Number.',
    'Print your Placement Form and the Enrolment Form from the portal.',
    'Visit the school campus with your printed forms and BECE result slip for verification.',
    'Complete the internal school registration forms and pick up the official prospectus.',
    'Finalize enrollment by attending the orientation session and receiving house assignments.',
]


def home(request):
    context = {
        'programmes': Programme.objects.all(),
        'features': FEATURES,
        'stats': STATS,
        'news_items': NewsItem.objects.all()[:2], # Fetch latest 2 news items
    }
    return render(request, 'school/home.html', context)


def about(request):
    context = {
        'values': [
            'Academic excellence rooted in strong teaching and consistent support.',
            'Leadership development through service, responsibility, and teamwork.',
            'A nurturing environment where every learner is known and encouraged.',
        ],
        'milestones': [
            'Founded to provide a balanced, future-ready education for growing families.',
            'Expanded into a full basic and secondary programme with modern learning spaces.',
            'Recognized for strong academic results and student development initiatives.',
        ],
        'facilities': Facility.objects.all(),
    }
    return render(request, 'school/about.html', context)


def academics(request):
    context = {
        'programmes': Programme.objects.prefetch_related('subjects').all(),
        'core_subjects': [
            'English Language',
            'Core Mathematics',
            'Integrated Science',
            'Social Studies',
        ],
        'highlights': [
            'WASSCE focused curriculum with intensive practical laboratory sessions.',
            'ICT integrated learning across all elective departments.',
            'Regular mock examinations and academic counseling for university placement.',
        ],
    }
    return render(request, 'school/academics.html', context)


def admissions(request):
    context = {
        'programmes': Programme.objects.all(),
        'steps': ADMISSION_STEPS,
        'requirements': [
            'CSSPS Placement and Enrolment forms (Printed)',
            'Original and photocopies of BECE Result Slip',
            'Certified Birth Certificate or NHIS card',
            'Six (6) recent passport-sized photographs',
            'Completed medical report from a recognized facility',
        ],
    }
    return render(request, 'school/admissions.html', context)


def news(request):
    return render(request, 'school/news.html', {'news_items': NewsItem.objects.all()}) # Fetch all news items


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(
                request,
                'Thanks for reaching out. Your message has been received and the admissions team will contact you soon.',
            )
            return redirect('contact')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'contact_details': {
            'address': '12 Learning Avenue, Greenfield Estate',
            'phone': '+234 800 123 4567',
            'email': 'admissions@zionschool.edu',
            'hours': 'Monday to Friday, 8:00 AM - 4:00 PM',
        },
    }
    return render(request, 'school/contact.html', context)
