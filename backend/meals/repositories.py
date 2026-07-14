from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List

from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import DailyMeal, Food, Meal, MealPlan, MealSettings, MealSuggestion, MealType


@dataclass(frozen=True)
class MealSettingsData:
    """Which meal types and weekdays a plan has enabled, with typed lookups.

    A value object the service owns so generation logic stays type-checkable —
    no dynamic getattr against ORM field names.
    """

    breakfast_enabled: bool
    lunch_enabled: bool
    dinner_enabled: bool
    snack_enabled: bool
    monday_enabled: bool
    tuesday_enabled: bool
    wednesday_enabled: bool
    thursday_enabled: bool
    friday_enabled: bool
    saturday_enabled: bool
    sunday_enabled: bool

    def enabled_meal_types(self) -> list[str]:
        enabled: list[str] = []
        if self.breakfast_enabled:
            enabled.append(MealType.BREAKFAST)
        if self.lunch_enabled:
            enabled.append(MealType.LUNCH)
        if self.dinner_enabled:
            enabled.append(MealType.DINNER)
        if self.snack_enabled:
            enabled.append(MealType.SNACK)
        return enabled

    def is_week_day_enabled(self, isoweekday: int) -> bool:
        if isoweekday == 1:
            return self.monday_enabled
        if isoweekday == 2:
            return self.tuesday_enabled
        if isoweekday == 3:
            return self.wednesday_enabled
        if isoweekday == 4:
            return self.thursday_enabled
        if isoweekday == 5:
            return self.friday_enabled
        if isoweekday == 6:
            return self.saturday_enabled
        if isoweekday == 7:
            return self.sunday_enabled
        raise ValueError(f"Not a valid ISO weekday: {isoweekday}")

    def get_enabled_days(self, from_date: date, to_date: date) -> list[date]:
        enabled_days: list[date] = []
        current_date = from_date
        while current_date <= to_date:
            if self.is_week_day_enabled(current_date.isoweekday()):
                enabled_days.append(current_date)
            current_date += timedelta(days=1)
        return enabled_days


@dataclass(frozen=True)
class FoodData:
    """A food value object; the only shape that crosses the Food repository boundary."""

    id: int
    name: str
    category: str
    created_at: datetime


@dataclass(frozen=True)
class MealSuggestionData:
    """A meal suggestion value object, with its foods already resolved to value objects."""

    id: int
    name: str
    description: str
    foods: list[FoodData]
    meal_type: str
    is_healthy: bool
    created_at: datetime


class MealPlanRepository:
    def for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return MealPlan.objects.filter(user_id=user_id)


class MealRepository:
    def for_user(
        self,
        user_id: int,
        name: str | None = None,
    ) -> QuerySet[Meal]:
        queryset: QuerySet[Meal] = Meal.objects.filter(user_id=user_id)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def create(
        self,
        user: User | None,
        name: str,
        notes: str = "",
        foods: QuerySet[Food] | None = None,
    ) -> Meal:
        meal = Meal.objects.create(user=user, name=name, notes=notes)
        if foods is not None:
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

    def delete_for_plan(self, meal_plan: MealPlan) -> None:
        meal_plan.daily_meals.all().delete()

    def get_or_create(
        self,
        meal_plan: MealPlan,
        meal_date: date,
        meal_type: str,
    ) -> tuple[DailyMeal, bool]:
        return DailyMeal.objects.get_or_create(
            meal_plan=meal_plan,
            date=meal_date,
            meal_type=meal_type,
        )

    def save(self, daily_meal: DailyMeal) -> None:
        daily_meal.save()


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

    def get_or_create_for_plan(self, meal_plan: MealPlan) -> MealSettingsData:
        meal_settings, _ = MealSettings.objects.get_or_create(meal_plan=meal_plan)
        return self._to_meal_settings_data(meal_settings)

    def _to_meal_settings_data(self, meal_settings: MealSettings) -> MealSettingsData:
        return MealSettingsData(
            breakfast_enabled=meal_settings.breakfast_enabled,
            lunch_enabled=meal_settings.lunch_enabled,
            dinner_enabled=meal_settings.dinner_enabled,
            snack_enabled=meal_settings.snack_enabled,
            monday_enabled=meal_settings.monday_enabled,
            tuesday_enabled=meal_settings.tuesday_enabled,
            wednesday_enabled=meal_settings.wednesday_enabled,
            thursday_enabled=meal_settings.thursday_enabled,
            friday_enabled=meal_settings.friday_enabled,
            saturday_enabled=meal_settings.saturday_enabled,
            sunday_enabled=meal_settings.sunday_enabled,
        )


class FoodRepository:
    def all(self) -> List[FoodData]:
        return [self._to_data(food) for food in Food.objects.all()]

    def search(self, query: str, limit: int = 10) -> List[FoodData]:
        foods = Food.objects.filter(name__icontains=query)[:limit]
        return [self._to_data(food) for food in foods]

    def get(self, food_id: int) -> FoodData | None:
        try:
            food = Food.objects.get(id=food_id)
        except Food.DoesNotExist:
            return None
        return self._to_data(food)

    def create(self, name: str, category: str) -> FoodData:
        food = Food.objects.create(name=name, category=category)
        return self._to_data(food)

    def update(self, food_id: int, name: str, category: str) -> FoodData | None:
        try:
            food = Food.objects.get(id=food_id)
        except Food.DoesNotExist:
            return None
        food.name = name
        food.category = category
        food.save()
        return self._to_data(food)

    def delete(self, food_id: int) -> bool:
        deleted_count, _ = Food.objects.filter(id=food_id).delete()
        return deleted_count > 0

    def _to_data(self, food: Food) -> FoodData:
        return FoodData(
            id=food.id,
            name=food.name,
            category=food.category,
            created_at=food.created_at,
        )


class MealSuggestionRepository:
    def list(
        self,
        meal_type: str | None = None,
        is_healthy: bool | None = None,
        limit: int | None = None,
    ) -> QuerySet[MealSuggestion]:
        """Return the ORM queryset directly.

        Kept for `MealPlanGenerationService`, which still walks ORM
        `MealSuggestion`/`Meal` relationships during generation. This is an
        accepted, tracked exception to the value-object boundary below —
        every other caller must use `list_data`/`get_data` instead.
        """
        queryset: QuerySet[MealSuggestion] = MealSuggestion.objects.all()
        if meal_type is not None:
            queryset = queryset.filter(meal_type=meal_type)
        if is_healthy is not None:
            queryset = queryset.filter(is_healthy=is_healthy)
        if limit is not None:
            queryset = queryset[:limit]
        return queryset

    def list_data(
        self,
        meal_type: str | None = None,
        is_healthy: bool | None = None,
    ) -> List[MealSuggestionData]:
        suggestions = self.list(meal_type=meal_type, is_healthy=is_healthy)
        return [self._to_data(suggestion) for suggestion in suggestions]

    def get_data(self, suggestion_id: int) -> MealSuggestionData | None:
        try:
            suggestion = MealSuggestion.objects.get(id=suggestion_id)
        except MealSuggestion.DoesNotExist:
            return None
        return self._to_data(suggestion)

    def _to_data(self, suggestion: MealSuggestion) -> MealSuggestionData:
        return MealSuggestionData(
            id=suggestion.id,
            name=suggestion.name,
            description=suggestion.description,
            foods=[self._to_food_data(food) for food in suggestion.foods.all()],
            meal_type=suggestion.meal_type,
            is_healthy=suggestion.is_healthy,
            created_at=suggestion.created_at,
        )

    def _to_food_data(self, food: Food) -> FoodData:
        return FoodData(
            id=food.id,
            name=food.name,
            category=food.category,
            created_at=food.created_at,
        )
