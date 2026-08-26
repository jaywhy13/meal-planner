from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0012_backfill_meal_plan_user_from_first_user"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="dailymeal",
            unique_together={("user", "meal_plan", "date", "meal_type")},
        ),
    ]
