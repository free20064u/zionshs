from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0005_update_responsibility_titles'),
        ('students', '0007_alter_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolclass',
            name='form_teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='form_classes',
                to='teachers.teacher',
            ),
        ),
    ]
