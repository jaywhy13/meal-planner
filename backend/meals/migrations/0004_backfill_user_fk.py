from django.db import migrations


def assign_existing_rows_to_first_superuser(apps, schema_editor):
    User = apps.get_model("auth", "User")
    MealPlan = apps.get_model("meals", "MealPlan")

    superuser = User.objects.filter(is_superuser=True).first()
    if superuser is None:
        return

    MealPlan.objects.filter(user=None).update(user=superuser)


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0003_add_user_fk_to_mealplan_food"),
    ]

    operations = [
        migrations.RunPython(
            assign_existing_rows_to_first_superuser,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
