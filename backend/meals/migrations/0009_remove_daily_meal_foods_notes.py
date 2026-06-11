from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0008_backfill_meal_from_daily_meal"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dailymeal",
            name="foods",
        ),
        migrations.RemoveField(
            model_name="dailymeal",
            name="notes",
        ),
    ]
