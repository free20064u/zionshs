import django.db.models.deletion
import re
from django.db import migrations, models


CLASS_PATTERN = re.compile(
    r'^(Science|Business|Agriculture|Home Economics|Visual Arts|General Arts)-([A-Z])-([0-9]{2})$'
)


def migrate_current_class_to_school_class(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    SchoolClass = apps.get_model('students', 'SchoolClass')

    for student in Student.objects.exclude(current_class='').exclude(current_class__isnull=True):
        match = CLASS_PATTERN.match(student.current_class.strip())
        if not match:
            continue

        programme, stream, year_suffix = match.groups()
        registration_year = 2000 + int(year_suffix)
        school_class, _ = SchoolClass.objects.get_or_create(
            programme=programme,
            stream=stream,
            registration_year=registration_year,
            defaults={'name': f'{programme}-{stream}-{year_suffix}'},
        )
        student.school_class = school_class
        student.save(update_fields=['school_class'])


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_seed_official_houses_and_relax_house_requirement'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programme', models.CharField(choices=[('Science', 'Science'), ('Business', 'Business'), ('Agriculture', 'Agriculture'), ('Home Economics', 'Home Economics'), ('Visual Arts', 'Visual Arts'), ('General Arts', 'General Arts')], max_length=30)),
                ('stream', models.CharField(max_length=1)),
                ('registration_year', models.PositiveSmallIntegerField(help_text='Full registration year, for example 2026.')),
                ('name', models.CharField(editable=False, max_length=50, unique=True)),
            ],
            options={
                'ordering': ['registration_year', 'programme', 'stream'],
                'constraints': [models.UniqueConstraint(fields=('programme', 'stream', 'registration_year'), name='unique_school_class_stream_per_year')],
            },
        ),
        migrations.AddField(
            model_name='student',
            name='school_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='students.schoolclass'),
        ),
        migrations.RunPython(migrate_current_class_to_school_class, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='student',
            name='current_class',
        ),
    ]
