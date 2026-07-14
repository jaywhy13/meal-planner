from __future__ import annotations

import calendar
from datetime import date

from django.db.models import QuerySet

from .models import DailyMeal, Meal, MealPlan, MealSettings, MealSuggestion
from .repositories import (
    DailyMealRepository,
    FoodData,
    FoodRepository,
    MealPlanRepository,
    MealRepository,
    MealSettingsData,
    MealSettingsRepository,
    MealSuggestionData,
    MealSuggestionRepository,
)


class MealPlanService:
    def __init__(
        self,
        meal_plan_repository: MealPlanRepository | None = None,
    ) -> None:
        self.meal_plan_repository = meal_plan_repository or MealPlanRepository()

    def list_for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return self.meal_plan_repository.for_user(user_id)


class MealService:
    def __init__(
        self,
        meal_repository: MealRepository | None = None,
    ) -> None:
        self.meal_repository = meal_repository or MealRepository()

    def list_for_user(
        self,
        user_id: int,
        name: str | None = None,
    ) -> QuerySet[Meal]:
        return self.meal_repository.for_user(user_id, name)


class DailyMealService:
    def __init__(
        self,
        daily_meal_repository: DailyMealRepository | None = None,
        meal_repository: MealRepository | None = None,
        meal_suggestion_repository: MealSuggestionRepository | None = None,
    ) -> None:
        self.daily_meal_repository = daily_meal_repository or DailyMealRepository()
        self.meal_repository = meal_repository or MealRepository()
        self.meal_suggestion_repository = meal_suggestion_repository or MealSuggestionRepository()

    def list_for_user(
        self,
        user_id: int,
        meal_plan_id: int | None = None,
    ) -> QuerySet[DailyMeal]:
        return self.daily_meal_repository.for_user(user_id, meal_plan_id)

    def get_or_create_daily_meal(
        self,
        meal_plan: MealPlan,
        meal_date: date,
        meal_type: str,
        meal: Meal | None = None,
    ) -> tuple[DailyMeal, bool]:
        """Ensure a daily meal exists for the date and type, attaching `meal` when fresh.

        Returns the daily meal and whether it was newly created. An existing
        daily meal is left untouched. Public so other flows (imports,
        background jobs) can reuse it, not just generation.
        """
        daily_meal, created = self.daily_meal_repository.get_or_create(meal_plan, meal_date, meal_type)
        if created and meal is not None:
            daily_meal.meal = meal
            self.daily_meal_repository.save(daily_meal)
        return daily_meal, created

    def meal_from_suggestion(self, meal_plan: MealPlan, suggestion: MealSuggestion) -> Meal:
        return self.meal_repository.create(
            user=meal_plan.user,
            name=suggestion.name,
            notes=suggestion.description,
            foods=suggestion.foods.all(),
        )


class MealPlanGenerationService:
    """Fills a meal plan's calendar month, reusing one Meal per suggestion per run."""

    def __init__(
        self,
        meal_settings_repository: MealSettingsRepository | None = None,
        daily_meal_repository: DailyMealRepository | None = None,
        meal_suggestion_repository: MealSuggestionRepository | None = None,
        daily_meal_service: DailyMealService | None = None,
    ) -> None:
        self.meal_settings_repository = meal_settings_repository or MealSettingsRepository()
        self.daily_meal_repository = daily_meal_repository or DailyMealRepository()
        self.meal_suggestion_repository = meal_suggestion_repository or MealSuggestionRepository()
        self.daily_meal_service = daily_meal_service or DailyMealService()

    def generate(self, meal_plan: MealPlan, wipe: bool = False) -> None:
        meal_settings = self.meal_settings_repository.get_or_create_for_plan(meal_plan)
        if wipe:
            self.daily_meal_repository.delete_for_plan(meal_plan)

        meal_by_suggestion_id: dict[int, Meal] = {}
        for current_date in self._enabled_dates(meal_plan, meal_settings):
            for meal_type in meal_settings.enabled_meal_types():
                self._fill_day(meal_plan, current_date, meal_type, meal_by_suggestion_id)

    def _enabled_dates(self, meal_plan: MealPlan, meal_settings: MealSettingsData) -> list[date]:
        month_start = meal_plan.start_date.replace(day=1)
        _, days_in_month = calendar.monthrange(month_start.year, month_start.month)
        month_end = month_start.replace(day=days_in_month)
        return meal_settings.get_enabled_days(month_start, month_end)

    def _fill_day(
        self,
        meal_plan: MealPlan,
        current_date: date,
        meal_type: str,
        meal_by_suggestion_id: dict[int, Meal],
    ) -> None:
        meal = self._suggested_meal(meal_plan, meal_type, meal_by_suggestion_id)
        self.daily_meal_service.get_or_create_daily_meal(meal_plan, current_date, meal_type, meal=meal)

    def _suggested_meal(
        self,
        meal_plan: MealPlan,
        meal_type: str,
        meal_by_suggestion_id: dict[int, Meal],
    ) -> Meal | None:
        suggestion = self.meal_suggestion_repository.list(meal_type=meal_type, is_healthy=True).first()
        if suggestion is None:
            return None

        meal = meal_by_suggestion_id.get(suggestion.id)
        if meal is None:
            meal = self.daily_meal_service.meal_from_suggestion(meal_plan, suggestion)
            meal_by_suggestion_id[suggestion.id] = meal
        return meal


class MealSuggestionService:
    def __init__(
        self,
        meal_suggestion_repository: MealSuggestionRepository | None = None,
    ) -> None:
        self.meal_suggestion_repository = meal_suggestion_repository or MealSuggestionRepository()

    def list_healthy(self, meal_type: str | None = None) -> list[MealSuggestionData]:
        return self.meal_suggestion_repository.list_data(meal_type=meal_type, is_healthy=True)

    def get(self, suggestion_id: int) -> MealSuggestionData | None:
        return self.meal_suggestion_repository.get_data(suggestion_id)


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


class FoodService:
    """Owns the search behaviour so blank-query and the result cap live in one place."""

    SEARCH_RESULT_LIMIT = 10

    def __init__(
        self,
        food_repository: FoodRepository | None = None,
    ) -> None:
        self.food_repository = food_repository or FoodRepository()

    def list_all(self) -> list[FoodData]:
        return self.food_repository.all()

    def search(self, query: str) -> list[FoodData]:
        if not query:
            return self.food_repository.all()[: self.SEARCH_RESULT_LIMIT]
        return self.food_repository.search(query, limit=self.SEARCH_RESULT_LIMIT)

    def get(self, food_id: int) -> FoodData | None:
        return self.food_repository.get(food_id)

    def create(self, name: str, category: str) -> FoodData:
        return self.food_repository.create(name, category)

    def update(self, food_id: int, name: str, category: str) -> FoodData | None:
        return self.food_repository.update(food_id, name, category)

    def delete(self, food_id: int) -> bool:
        return self.food_repository.delete(food_id)
