from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_subject_programme'),
        ('students', '0008_house_color'),
        ('teachers', '0006_alter_responsibility_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='classes_taught',
            field=models.ManyToManyField(blank=True, related_name='subject_teachers', to='students.schoolclass'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='house',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='house_teachers', to='students.house'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='subjects_taught',
            field=models.ManyToManyField(blank=True, related_name='teachers', to='school.subject'),
        ),
    ]
