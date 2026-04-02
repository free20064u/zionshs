from django.db import migrations


def backfill_user_roles(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')

    CustomUser.objects.filter(is_student=True).update(role='Student')
    CustomUser.objects.filter(is_teacher=True).update(role='Teacher')
    CustomUser.objects.filter(is_student=False, is_teacher=False).update(role='')


def reverse_backfill_user_roles(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    CustomUser.objects.filter(role='Student').update(is_student=True, is_teacher=False)
    CustomUser.objects.filter(role='Teacher').update(is_teacher=True, is_student=False)
    CustomUser.objects.filter(role='').update(is_student=False, is_teacher=False)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_role'),
    ]

    operations = [
        migrations.RunPython(backfill_user_roles, reverse_backfill_user_roles),
    ]
