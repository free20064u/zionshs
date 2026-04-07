from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0005_update_responsibility_titles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsibility',
            name='title',
            field=models.CharField(max_length=120, unique=True),
        ),
    ]
