from __future__ import annotations

from typing import Iterable

from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import DailyMeal, Food, Meal, MealPlan, MealSettings


class MealPlanRepository:
    def for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return MealPlan.objects.filter(user_id=user_id)


class MealRepository:
    def for_user(self, user_id: int, name_search: str | None = None) -> QuerySet[Meal]:
        queryset: QuerySet[Meal] = Meal.objects.filter(user_id=user_id)
        if name_search:
            queryset = queryset.filter(name__icontains=name_search)
        return queryset

    def create_with_foods(
        self,
        owner: User | None,
        name: str,
        notes: str,
        foods: Iterable[Food],
    ) -> Meal:
        meal = Meal.objects.create(user=owner, name=name, notes=notes)
        meal.foods.set(foods)
        return meal


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
