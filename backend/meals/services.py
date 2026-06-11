from __future__ import annotations

import calendar
from datetime import date, timedelta

from django.db.models import QuerySet

from .models import DailyMeal, Meal, MealPlan, MealSettings, MealSuggestion
from .repositories import (
    DailyMealRepository,
    MealPlanRepository,
    MealRepository,
    MealSettingsRepository,
)

ISO_WEEKDAY_TO_SETTINGS_FIELD = {
    1: "monday_enabled",
    2: "tuesday_enabled",
    3: "wednesday_enabled",
    4: "thursday_enabled",
    5: "friday_enabled",
    6: "saturday_enabled",
    7: "sunday_enabled",
}

MEAL_TYPE_TO_SETTINGS_FIELD = {
    "breakfast": "breakfast_enabled",
    "lunch": "lunch_enabled",
    "dinner": "dinner_enabled",
    "snack": "snack_enabled",
}


class MealPlanService:
    def __init__(
        self,
        meal_plan_repository: MealPlanRepository | None = None,
        meal_repository: MealRepository | None = None,
    ) -> None:
        self.meal_plan_repository = meal_plan_repository or MealPlanRepository()
        self.meal_repository = meal_repository or MealRepository()

    def list_for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return self.meal_plan_repository.for_user(user_id)

    def generate_meals(self, meal_plan: MealPlan, wipe: bool) -> None:
        meal_settings, _ = MealSettings.objects.get_or_create(meal_plan=meal_plan)
        if wipe:
            meal_plan.daily_meals.all().delete()

        enabled_meal_types = self._enabled_meal_types(meal_settings)
        reusable_meal_by_suggestion: dict[int, Meal] = {}
        for current_date in self._enabled_dates(meal_plan, meal_settings):
            for meal_type in enabled_meal_types:
                self._fill_slot(meal_plan, current_date, meal_type, reusable_meal_by_suggestion)

    def _fill_slot(
        self,
        meal_plan: MealPlan,
        current_date: date,
        meal_type: str,
        reusable_meal_by_suggestion: dict[int, Meal],
    ) -> None:
        daily_meal, created = DailyMeal.objects.get_or_create(
            meal_plan=meal_plan,
            date=current_date,
            meal_type=meal_type,
        )
        if not created:
            return
        suggestion = self._suggestion_for(meal_type)
        if suggestion is None:
            return
        daily_meal.meal = self._reusable_meal_for(meal_plan, suggestion, reusable_meal_by_suggestion)
        daily_meal.save(update_fields=["meal"])

    def _reusable_meal_for(
        self,
        meal_plan: MealPlan,
        suggestion: MealSuggestion,
        reusable_meal_by_suggestion: dict[int, Meal],
    ) -> Meal:
        existing = reusable_meal_by_suggestion.get(suggestion.id)
        if existing is not None:
            return existing
        meal = self.meal_repository.create_with_foods(
            owner=meal_plan.user,
            name=suggestion.name,
            notes=suggestion.description,
            foods=suggestion.foods.all(),
        )
        reusable_meal_by_suggestion[suggestion.id] = meal
        return meal

    def _suggestion_for(self, meal_type: str) -> MealSuggestion | None:
        # Deterministically pick the lowest-id healthy suggestion so the same
        # meal type always yields the same suggestion across runs and databases.
        return (
            MealSuggestion.objects.filter(is_healthy=True, meal_type=meal_type)
            .order_by("id")
            .first()
        )

    def _enabled_meal_types(self, meal_settings: MealSettings) -> list[str]:
        return [
            meal_type
            for meal_type, settings_field in MEAL_TYPE_TO_SETTINGS_FIELD.items()
            if getattr(meal_settings, settings_field)
        ]

    def _enabled_dates(self, meal_plan: MealPlan, meal_settings: MealSettings) -> list[date]:
        start = meal_plan.start_date.replace(day=1)
        _, days_in_month = calendar.monthrange(start.year, start.month)
        enabled_dates: list[date] = []
        for offset in range(days_in_month):
            current_date = start + timedelta(days=offset)
            settings_field = ISO_WEEKDAY_TO_SETTINGS_FIELD[current_date.isoweekday()]
            if getattr(meal_settings, settings_field):
                enabled_dates.append(current_date)
        return enabled_dates


class MealService:
    def __init__(
        self,
        meal_repository: MealRepository | None = None,
    ) -> None:
        self.meal_repository = meal_repository or MealRepository()

    def list_for_user(self, user_id: int, name_search: str | None = None) -> QuerySet[Meal]:
        return self.meal_repository.for_user(user_id, name_search)


class DailyMealService:
    def __init__(
        self,
        daily_meal_repository: DailyMealRepository | None = None,
    ) -> None:
        self.daily_meal_repository = daily_meal_repository or DailyMealRepository()

    def list_for_user(
        self,
        user_id: int,
        meal_plan_id: int | None = None,
    ) -> QuerySet[DailyMeal]:
        return self.daily_meal_repository.for_user(user_id, meal_plan_id)


class MealSettingsService:
    def __init__(
        self,
        meal_settings_repository: MealSettingsRepository | None = None,
    ) -> None:
        self.meal_settings_repository = meal_settings_repository or MealSettingsRepository()

    def list_for_user(
        self,
        user_id: int,
        meal_plan_id: int | None = None,
    ) -> QuerySet[MealSettings]:
        return self.meal_settings_repository.for_user(user_id, meal_plan_id)
