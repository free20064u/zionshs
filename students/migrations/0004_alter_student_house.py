from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_seed_default_house'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='house',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='students', to='students.house'),
        ),
    ]
