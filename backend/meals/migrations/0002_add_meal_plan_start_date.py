import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealplan',
            name='start_date',
            field=models.DateField(default=datetime.date(2026, 1, 1)),
            preserve_default=False,
        ),
    ]
