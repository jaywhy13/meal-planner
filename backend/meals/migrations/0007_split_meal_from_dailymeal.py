import django.db.models.deletion
from django.db import migrations, models


def extract_reusable_meals(apps, schema_editor):
    """Move each DailyMeal's foods/notes into a dedicated reusable Meal and link it back."""
    DailyMeal = apps.get_model("meals", "DailyMeal")
    Meal = apps.get_model("meals", "Meal")

    for daily_meal in DailyMeal.objects.all():
        meal = Meal.objects.create(notes=daily_meal.notes)
        meal.foods.set(daily_meal.foods.all())
        daily_meal.meal = meal
        daily_meal.save(update_fields=["meal"])


class Migration(migrations.Migration):
    dependencies = [
        ("meals", "0006_dailymeal_date_day_of_week"),
    ]

    operations = [
        migrations.CreateModel(
            name="Meal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notes", models.TextField(blank=True)),
                ("foods", models.ManyToManyField(blank=True, to="meals.food")),
            ],
        ),
        migrations.AddField(
            model_name="dailymeal",
            name="meal",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="daily_meals",
                to="meals.meal",
            ),
        ),
        migrations.RunPython(extract_reusable_meals, migrations.RunPython.noop),
        migrations.RemoveField(model_name="dailymeal", name="foods"),
        migrations.RemoveField(model_name="dailymeal", name="notes"),
    ]
