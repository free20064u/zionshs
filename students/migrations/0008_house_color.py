from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_schoolclass_form_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='color',
            field=models.CharField(default='#6c757d', max_length=7),
        ),
    ]
