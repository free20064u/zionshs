from django.db import migrations, models


OLD_TO_NEW_TITLES = {
    'Headteacher Academics': 'Assistant Headteacher Academic',
    'Headteacher Domestic': 'Assistant Headteacher Domestic',
    'Headteacher Administration': 'Assistant Headteacher Administration',
}

VALID_TITLES = {
    'Headteacher',
    'Assistant Headteacher Academic',
    'Assistant Headteacher Domestic',
    'Assistant Headteacher Administration',
    'Head of Department',
    'Senior House Teacher',
    'House Teacher',
}


def migrate_responsibility_titles(apps, schema_editor):
    Responsibility = apps.get_model('teachers', 'Responsibility')

    for old_title, new_title in OLD_TO_NEW_TITLES.items():
        try:
            responsibility = Responsibility.objects.get(title=old_title)
        except Responsibility.DoesNotExist:
            continue
        responsibility.title = new_title
        responsibility.save(update_fields=['title'])

    Responsibility.objects.filter(title__in=['Dean of Discipline', 'Form Teacher']).delete()

    for title in VALID_TITLES:
        Responsibility.objects.get_or_create(title=title, defaults={'description': ''})


def reverse_migrate_responsibility_titles(apps, schema_editor):
    Responsibility = apps.get_model('teachers', 'Responsibility')

    reverse_map = {value: key for key, value in OLD_TO_NEW_TITLES.items()}
    for new_title, old_title in reverse_map.items():
        try:
            responsibility = Responsibility.objects.get(title=new_title)
        except Responsibility.DoesNotExist:
            continue
        responsibility.title = old_title
        responsibility.save(update_fields=['title'])

    for title in ['Dean of Discipline', 'Form Teacher']:
        Responsibility.objects.get_or_create(title=title, defaults={'description': ''})


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0004_alter_teacher_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsibility',
            name='title',
            field=models.CharField(
                choices=[
                    ('Headteacher', 'Headteacher'),
                    ('Assistant Headteacher Academic', 'Assistant Headteacher Academic'),
                    ('Assistant Headteacher Domestic', 'Assistant Headteacher Domestic'),
                    ('Assistant Headteacher Administration', 'Assistant Headteacher Administration'),
                    ('Head of Department', 'Head of Department'),
                    ('Senior House Teacher', 'Senior House Teacher'),
                    ('House Teacher', 'House Teacher'),
                ],
                max_length=120,
                unique=True,
            ),
        ),
        migrations.RunPython(migrate_responsibility_titles, reverse_migrate_responsibility_titles),
    ]
