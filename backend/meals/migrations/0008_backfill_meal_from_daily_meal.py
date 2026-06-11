from django.db import migrations


def is_non_empty(daily_meal) -> bool:
    return daily_meal.notes.strip() != "" or daily_meal.foods.exists()


def generated_name_for(daily_meal) -> str:
    meal_type_label = daily_meal.meal_type.capitalize()
    return f"{meal_type_label} on {daily_meal.date.isoformat()}"


def extract_meal_per_non_empty_daily_meal(apps, schema_editor):
    DailyMeal = apps.get_model("meals", "DailyMeal")
    Meal = apps.get_model("meals", "Meal")

    for daily_meal in DailyMeal.objects.select_related("meal_plan").all():
        if not is_non_empty(daily_meal):
            continue
        meal = Meal.objects.create(
            user=daily_meal.meal_plan.user,
            name=generated_name_for(daily_meal),
            notes=daily_meal.notes,
        )
        meal.foods.set(daily_meal.foods.all())
        daily_meal.meal = meal
        daily_meal.save(update_fields=["meal"])


def move_foods_and_notes_back_to_daily_meal(apps, schema_editor):
    """Reverse of the backfill: copy each linked Meal's foods/notes back onto its
    slots, unlink, then delete the Meal rows so a down/up replay stays idempotent
    (no orphaned Meals, no duplicate creation on re-apply).

    Faithfulness caveat: the forward migration creates one Meal per non-empty slot,
    so at that point the inverse is exact. If meals have since been *shared* across
    slots (the feature's whole point), the shared Meal's single notes value is copied
    onto every slot it backs — per-slot notes can't be reconstructed once collapsed.
    """
    DailyMeal = apps.get_model("meals", "DailyMeal")
    Meal = apps.get_model("meals", "Meal")

    linked_meal_ids: set[int] = set()
    for daily_meal in DailyMeal.objects.select_related("meal").all():
        meal = daily_meal.meal
        if meal is None:
            continue
        daily_meal.notes = meal.notes
        daily_meal.meal = None
        daily_meal.save(update_fields=["notes", "meal"])
        daily_meal.foods.set(meal.foods.all())
        linked_meal_ids.add(meal.id)

    Meal.objects.filter(id__in=linked_meal_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0007_add_meal_model"),
    ]

    operations = [
        migrations.RunPython(
            extract_meal_per_non_empty_daily_meal,
            reverse_code=move_foods_and_notes_back_to_daily_meal,
        ),
    ]
