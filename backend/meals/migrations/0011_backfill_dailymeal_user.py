from django.db import migrations

from ._daily_meal_user_backfill import backfill_daily_meals_missing_user


def backfill_daily_meal_user_from_meal_plan(apps, schema_editor):
    MealPlan = apps.get_model("meals", "MealPlan")
    DailyMeal = apps.get_model("meals", "DailyMeal")

    backfill_daily_meals_missing_user(MealPlan, DailyMeal)


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0010_add_user_fk_to_dailymeal"),
    ]

    operations = [
        migrations.RunPython(
            backfill_daily_meal_user_from_meal_plan,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
