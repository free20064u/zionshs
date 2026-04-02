from django.db import migrations


DEFAULT_HOUSE_NAME = 'Unassigned House'


def seed_default_house(apps, schema_editor):
    House = apps.get_model('students', 'House')
    Student = apps.get_model('students', 'Student')

    house, _ = House.objects.get_or_create(
        name=DEFAULT_HOUSE_NAME,
        defaults={'description': 'Temporary default house for existing student records.'},
    )
    Student.objects.filter(house__isnull=True).update(house=house)


def unseed_default_house(apps, schema_editor):
    House = apps.get_model('students', 'House')
    House.objects.filter(name=DEFAULT_HOUSE_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_house_student_programme_student_house'),
    ]

    operations = [
        migrations.RunPython(seed_default_house, unseed_default_house),
    ]
