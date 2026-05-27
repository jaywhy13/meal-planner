from __future__ import annotations

from django.db.models import QuerySet

from .models import DailyMeal, MealPlan, MealSettings


class MealPlanRepository:
    def for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return MealPlan.objects.filter(user_id=user_id)


class DailyMealRepository:
    def for_user(
        self,
        user_id: int,
        meal_plan_id: int | None = None,
    ) -> QuerySet[DailyMeal]:
        queryset: QuerySet[DailyMeal] = DailyMeal.objects.filter(
            meal_plan__user_id=user_id,
        )
        if meal_plan_id is not None:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset


class MealSettingsRepository:
    def for_user(
        self,
        user_id: int,
        meal_plan_id: int | None = None,
    ) -> QuerySet[MealSettings]:
        queryset: QuerySet[MealSettings] = MealSettings.objects.filter(
            meal_plan__user_id=user_id,
        )
        if meal_plan_id is not None:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset
