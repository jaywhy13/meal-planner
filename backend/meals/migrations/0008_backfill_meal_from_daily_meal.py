from django.db import migrations


def generated_meal_name(daily_meal) -> str:
    return f"{daily_meal.meal_plan.name} - {daily_meal.date} - {daily_meal.meal_type}"


def create_meal_for_each_non_empty_daily_meal(apps, schema_editor):
    DailyMeal = apps.get_model("meals", "DailyMeal")
    Meal = apps.get_model("meals", "Meal")

    for daily_meal in DailyMeal.objects.all():
        food_ids = list(daily_meal.foods.values_list("id", flat=True))
        has_content = bool(food_ids) or bool(daily_meal.notes)
        if not has_content:
            continue

        meal = Meal.objects.create(
            user=daily_meal.meal_plan.user,
            name=generated_meal_name(daily_meal),
            notes=daily_meal.notes,
        )
        meal.foods.set(food_ids)
        daily_meal.meal = meal
        daily_meal.save(update_fields=["meal"])


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0007_add_meal_model"),
    ]

    operations = [
        migrations.RunPython(
            create_meal_for_each_non_empty_daily_meal,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
