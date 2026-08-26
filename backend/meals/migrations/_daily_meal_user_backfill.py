def backfill_daily_meals_missing_user(MealPlan, DailyMeal) -> None:
    """Copy `meal_plan.user` onto every owned plan's `DailyMeal` rows still missing a user.

    Shared by 0011 (initial backfill) and 0012 (re-run after newly assigning
    orphaned meal plans), which is why it takes already-resolved historical
    model classes rather than calling `apps.get_model` itself.
    """
    plans_with_owner_and_unowned_daily_meals = MealPlan.objects.filter(
        user__isnull=False,
        daily_meals__user__isnull=True,
    ).distinct()
    for meal_plan in plans_with_owner_and_unowned_daily_meals:
        DailyMeal.objects.filter(meal_plan=meal_plan, user__isnull=True).update(user=meal_plan.user)
