from django.db import migrations


DEFAULT_RESPONSIBILITIES = [
    'Headteacher',
    'Headteacher Academics',
    'Headteacher Domestic',
    'Headteacher Administration',
    'Dean of Discipline',
    'Head of Department',
    'Senior House Teacher',
    'House Teacher',
    'Form Teacher',
]


def seed_responsibilities(apps, schema_editor):
    Responsibility = apps.get_model('teachers', 'Responsibility')

    for title in DEFAULT_RESPONSIBILITIES:
        Responsibility.objects.get_or_create(title=title, defaults={'description': ''})


def unseed_responsibilities(apps, schema_editor):
    Responsibility = apps.get_model('teachers', 'Responsibility')
    Responsibility.objects.filter(title__in=DEFAULT_RESPONSIBILITIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0002_alter_responsibility_title'),
    ]

    operations = [
        migrations.RunPython(seed_responsibilities, unseed_responsibilities),
    ]
