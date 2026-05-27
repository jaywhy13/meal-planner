import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0005_add_meal_plan_start_date'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dailymeal',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='dailymeal',
            name='week',
        ),
        migrations.RemoveField(
            model_name='dailymeal',
            name='day',
        ),
        migrations.AddField(
            model_name='dailymeal',
            name='date',
            field=models.DateField(default=datetime.date(2026, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailymeal',
            name='day_of_week',
            field=models.PositiveSmallIntegerField(db_index=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='dailymeal',
            options={'ordering': ['date', 'meal_type']},
        ),
        migrations.AlterUniqueTogether(
            name='dailymeal',
            unique_together={('meal_plan', 'date', 'meal_type')},
        ),
    ]
