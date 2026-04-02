from django.db import migrations, models


OFFICIAL_HOUSES = [
    'House 1',
    'House 2',
    'House 3',
    'House 4',
]


def seed_official_houses(apps, schema_editor):
    House = apps.get_model('students', 'House')
    Student = apps.get_model('students', 'Student')

    for name in OFFICIAL_HOUSES:
        House.objects.get_or_create(name=name, defaults={'description': ''})

    Student.objects.filter(house__name='Unassigned House').update(house=None)
    House.objects.filter(name='Unassigned House').delete()


def unseed_official_houses(apps, schema_editor):
    House = apps.get_model('students', 'House')
    House.objects.filter(name__in=OFFICIAL_HOUSES).delete()
    House.objects.get_or_create(
        name='Unassigned House',
        defaults={'description': 'Temporary default house for existing student records.'},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_student_house'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='house',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name='students',
                to='students.house',
            ),
        ),
        migrations.RunPython(seed_official_houses, unseed_official_houses),
    ]
