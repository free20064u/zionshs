from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm


PROGRAMMES = [
    {
        'title': 'Early Years',
        'description': 'Play-based learning that develops language, confidence, and curiosity in a safe environment.',
    },
    {
        'title': 'Primary School',
        'description': 'Strong literacy, numeracy, science, and creative arts foundations supported by caring teachers.',
    },
    {
        'title': 'Secondary School',
        'description': 'Rigorous academics, leadership coaching, and career pathways that prepare students for university and beyond.',
    },
]

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

NEWS_ITEMS = [
    {
        'title': 'STEM Fair Showcases Student-Led Innovation',
        'summary': 'Learners presented robotics, renewable energy, and engineering prototypes to parents and local partners.',
        'date': 'March 18, 2026',
    },
    {
        'title': 'Admissions Open for the 2026/2027 Session',
        'summary': 'Families can now begin applications, book campus tours, and attend our open house sessions.',
        'date': 'February 10, 2026',
    },
    {
        'title': 'Inter-House Athletics Builds Team Spirit',
        'summary': 'Students competed across track, football, and relay events with an emphasis on discipline and sportsmanship.',
        'date': 'January 24, 2026',
    },
]

ADMISSION_STEPS = [
    'Complete the admission inquiry form or visit the school office.',
    'Attend a campus tour and family information session.',
    'Submit prior academic records and supporting documents.',
    'Take the placement assessment and meet with admissions staff.',
    'Receive an offer letter and complete enrollment.',
]


def home(request):
    context = {
        'programmes': PROGRAMMES,
        'features': FEATURES,
        'stats': STATS,
        'news_items': NEWS_ITEMS[:2],
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
    }
    return render(request, 'school/about.html', context)


def academics(request):
    context = {
        'programmes': PROGRAMMES,
        'highlights': [
            'Small classes that allow for attentive teaching and targeted feedback.',
            'Digital literacy, science practicals, and enrichment activities built into the timetable.',
            'Continuous assessment paired with clear reporting for families.',
        ],
    }
    return render(request, 'school/academics.html', context)


def admissions(request):
    context = {
        'steps': ADMISSION_STEPS,
        'requirements': [
            'Completed application form',
            'Passport photograph',
            'Birth certificate or valid identification',
            'Previous school report cards',
        ],
    }
    return render(request, 'school/admissions.html', context)


def news(request):
    return render(request, 'school/news.html', {'news_items': NEWS_ITEMS})


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
