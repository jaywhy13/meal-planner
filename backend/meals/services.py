from __future__ import annotations

import calendar
from datetime import date as date_type, timedelta

from django.db.models import QuerySet

from .models import MealPlan, MealSettings
from .repositories import (
    DailyMealRepository,
    MealPlanRepository,
    MealSettingsRepository,
    MealSuggestionRepository,
)
from .value_objects import DailyMealData


class MealPlanNotOwnedError(Exception):
    """Raised when a user acts on a meal plan they do not own."""


class MealPlanService:
    def __init__(
        self,
        meal_plan_repository: MealPlanRepository | None = None,
        daily_meal_repository: DailyMealRepository | None = None,
        meal_settings_repository: MealSettingsRepository | None = None,
        meal_suggestion_repository: MealSuggestionRepository | None = None,
    ) -> None:
        self.meal_plan_repository = meal_plan_repository or MealPlanRepository()
        self.daily_meal_repository = daily_meal_repository or DailyMealRepository()
        self.meal_settings_repository = meal_settings_repository or MealSettingsRepository()
        self.meal_suggestion_repository = meal_suggestion_repository or MealSuggestionRepository()

    def list_for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return self.meal_plan_repository.for_user(user_id)

    def detail_for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return self.meal_plan_repository.for_user_with_meals(user_id)

    def generate_meals(self, meal_plan_id: int, wipe: bool) -> None:
        flags = self.meal_settings_repository.ensure_flags_for_plan(meal_plan_id)
        suggestions = self.meal_suggestion_repository.healthy_content_by_meal_type()

        if wipe:
            self.daily_meal_repository.delete_for_plan(meal_plan_id)

        for current_date in self._dates_in_plan_month(meal_plan_id):
            if current_date.isoweekday() not in flags.enabled_iso_weekdays:
                continue
            for meal_type in flags.enabled_meal_types:
                content = suggestions.get(meal_type)
                self.daily_meal_repository.get_or_create_with_content(
                    meal_plan_id=meal_plan_id,
                    date=current_date,
                    meal_type=meal_type,
                    food_ids=content.food_ids if content else [],
                    notes=content.notes if content else "",
                )

    def _dates_in_plan_month(self, meal_plan_id: int) -> list[date_type]:
        start = self.meal_plan_repository.start_date(meal_plan_id).replace(day=1)
        _, days_in_month = calendar.monthrange(start.year, start.month)
        return [start + timedelta(days=offset) for offset in range(days_in_month)]


class DailyMealService:
    def __init__(
        self,
        daily_meal_repository: DailyMealRepository | None = None,
        meal_plan_repository: MealPlanRepository | None = None,
    ) -> None:
        self.daily_meal_repository = daily_meal_repository or DailyMealRepository()
        self.meal_plan_repository = meal_plan_repository or MealPlanRepository()

    def list_for_user(self, user_id: int, meal_plan_id: int | None = None) -> list[DailyMealData]:
        return self.daily_meal_repository.list_for_user(user_id, meal_plan_id)

    def create(
        self,
        user_id: int,
        meal_plan_id: int,
        date: date_type,
        meal_type: str,
        food_ids: list[int],
        notes: str,
    ) -> DailyMealData:
        self._assert_owns_plan(user_id, meal_plan_id)
        return self.daily_meal_repository.create(meal_plan_id, date, meal_type, food_ids, notes)

    def update(
        self,
        user_id: int,
        daily_meal_id: int,
        meal_plan_id: int,
        date: date_type,
        meal_type: str,
        food_ids: list[int],
        notes: str,
    ) -> DailyMealData:
        self._assert_owns_plan(user_id, meal_plan_id)
        return self.daily_meal_repository.update(
            daily_meal_id, meal_plan_id, date, meal_type, food_ids, notes
        )

    def delete(self, user_id: int, daily_meal_id: int) -> None:
        self.daily_meal_repository.delete_for_user(user_id, daily_meal_id)

    def get_for_user(self, user_id: int, daily_meal_id: int) -> DailyMealData | None:
        return self.daily_meal_repository.get_for_user(user_id, daily_meal_id)

    def _assert_owns_plan(self, user_id: int, meal_plan_id: int) -> None:
        if not self.meal_plan_repository.is_owned_by(meal_plan_id, user_id):
            raise MealPlanNotOwnedError()


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
