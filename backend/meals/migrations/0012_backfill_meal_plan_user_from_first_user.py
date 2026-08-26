from django.db import migrations

from ._daily_meal_user_backfill import backfill_daily_meals_missing_user


def assign_unowned_meal_plans_to_first_user(apps, schema_editor):
    User = apps.get_model("auth", "User")
    MealPlan = apps.get_model("meals", "MealPlan")
    DailyMeal = apps.get_model("meals", "DailyMeal")

    first_user = User.objects.order_by("id").first()
    if first_user is None:
        return

    MealPlan.objects.filter(user=None).update(user=first_user)
    backfill_daily_meals_missing_user(MealPlan, DailyMeal)


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0011_backfill_dailymeal_user"),
    ]

    operations = [
        migrations.RunPython(
            assign_unowned_meal_plans_to_first_user,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
