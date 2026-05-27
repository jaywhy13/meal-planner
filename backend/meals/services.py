from __future__ import annotations

from django.db.models import QuerySet

from .models import DailyMeal, MealPlan, MealSettings
from .repositories import DailyMealRepository, MealPlanRepository, MealSettingsRepository


class MealPlanService:
    def __init__(
        self,
        meal_plan_repository: MealPlanRepository | None = None,
    ) -> None:
        self.meal_plan_repository = meal_plan_repository or MealPlanRepository()

    def list_for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return self.meal_plan_repository.for_user(user_id)


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
