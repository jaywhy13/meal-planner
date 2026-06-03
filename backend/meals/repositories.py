from __future__ import annotations

from datetime import date as date_type

from django.db.models import QuerySet

from .models import DailyMeal, Meal, MealPlan, MealSettings, MealSuggestion
from .value_objects import DailyMealData, FoodData, MealSettingsFlags, SuggestionContent

_ISO_WEEKDAY_BY_DAY_FIELD = {
    "monday_enabled": 1,
    "tuesday_enabled": 2,
    "wednesday_enabled": 3,
    "thursday_enabled": 4,
    "friday_enabled": 5,
    "saturday_enabled": 6,
    "sunday_enabled": 7,
}

_MEAL_TYPE_BY_ENABLED_FIELD = {
    "breakfast_enabled": "breakfast",
    "lunch_enabled": "lunch",
    "dinner_enabled": "dinner",
    "snack_enabled": "snack",
}


class MealPlanRepository:
    def for_user(self, user_id: int) -> QuerySet[MealPlan]:
        return MealPlan.objects.filter(user_id=user_id)

    def for_user_with_meals(self, user_id: int) -> QuerySet[MealPlan]:
        return self.for_user(user_id).prefetch_related(
            "daily_meals__meal__foods",
            "meal_settings",
        )

    def is_owned_by(self, meal_plan_id: int, user_id: int) -> bool:
        return MealPlan.objects.filter(id=meal_plan_id, user_id=user_id).exists()

    def start_date(self, meal_plan_id: int) -> date_type:
        return MealPlan.objects.values_list("start_date", flat=True).get(id=meal_plan_id)


class DailyMealRepository:
    def list_for_user(self, user_id: int, meal_plan_id: int | None = None) -> list[DailyMealData]:
        queryset = self._for_user_queryset(user_id, meal_plan_id)
        return [self._to_data(daily_meal) for daily_meal in queryset]

    def get_for_user(self, user_id: int, daily_meal_id: int) -> DailyMealData | None:
        daily_meal = self._for_user_queryset(user_id).filter(id=daily_meal_id).first()
        return self._to_data(daily_meal) if daily_meal else None

    def create(
        self,
        meal_plan_id: int,
        date: date_type,
        meal_type: str,
        food_ids: list[int],
        notes: str,
    ) -> DailyMealData:
        daily_meal, _ = DailyMeal.objects.get_or_create(
            meal_plan_id=meal_plan_id,
            date=date,
            meal_type=meal_type,
        )
        self._assign_meal(daily_meal, food_ids, notes)
        return self._to_data(self._reload(daily_meal.id))

    def update(
        self,
        daily_meal_id: int,
        meal_plan_id: int,
        date: date_type,
        meal_type: str,
        food_ids: list[int],
        notes: str,
    ) -> DailyMealData:
        daily_meal = DailyMeal.objects.get(id=daily_meal_id)
        daily_meal.meal_plan_id = meal_plan_id
        daily_meal.date = date
        daily_meal.meal_type = meal_type
        daily_meal.save()
        self._assign_meal(daily_meal, food_ids, notes)
        return self._to_data(self._reload(daily_meal_id))

    def delete_for_user(self, user_id: int, daily_meal_id: int) -> None:
        self._for_user_queryset(user_id).filter(id=daily_meal_id).delete()

    def delete_for_plan(self, meal_plan_id: int) -> None:
        DailyMeal.objects.filter(meal_plan_id=meal_plan_id).delete()

    def get_or_create_with_content(
        self,
        meal_plan_id: int,
        date: date_type,
        meal_type: str,
        food_ids: list[int],
        notes: str,
    ) -> None:
        daily_meal, created = DailyMeal.objects.get_or_create(
            meal_plan_id=meal_plan_id,
            date=date,
            meal_type=meal_type,
        )
        if created:
            self._assign_meal(daily_meal, food_ids, notes)

    def _for_user_queryset(self, user_id: int, meal_plan_id: int | None = None) -> QuerySet[DailyMeal]:
        queryset = (
            DailyMeal.objects.filter(meal_plan__user_id=user_id)
            .select_related("meal")
            .prefetch_related("meal__foods")
        )
        if meal_plan_id is not None:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset

    def _reload(self, daily_meal_id: int) -> DailyMeal:
        return DailyMeal.objects.select_related("meal").prefetch_related("meal__foods").get(id=daily_meal_id)

    def _assign_meal(self, daily_meal: DailyMeal, food_ids: list[int], notes: str) -> None:
        if not food_ids and not notes:
            self._unlink_meal(daily_meal)
            return
        meal = self._writable_meal_for(daily_meal)
        meal.notes = notes
        meal.save()
        meal.foods.set(food_ids)
        if daily_meal.meal_id != meal.id:
            daily_meal.meal = meal
            daily_meal.save(update_fields=["meal"])

    def _writable_meal_for(self, daily_meal: DailyMeal) -> Meal:
        existing_meal = daily_meal.meal
        if existing_meal is None:
            return Meal()
        # Meals are reusable across slots; never mutate one another slot still links to.
        if existing_meal.daily_meals.count() > 1:
            return Meal()
        return existing_meal

    def _unlink_meal(self, daily_meal: DailyMeal) -> None:
        if daily_meal.meal_id is not None:
            daily_meal.meal = None
            daily_meal.save(update_fields=["meal"])

    def _to_data(self, daily_meal: DailyMeal) -> DailyMealData:
        meal = daily_meal.meal
        foods = [FoodData(id=food.id, name=food.name, category=food.category) for food in meal.foods.all()] if meal else []
        return DailyMealData(
            id=daily_meal.id,
            meal_plan_id=daily_meal.meal_plan_id,
            date=daily_meal.date,
            day_of_week=daily_meal.day_of_week,
            meal_type=daily_meal.meal_type,
            foods=foods,
            notes=meal.notes if meal else "",
        )


class MealSettingsRepository:
    def for_user(self, user_id: int, meal_plan_id: int | None = None) -> QuerySet[MealSettings]:
        queryset = MealSettings.objects.filter(meal_plan__user_id=user_id)
        if meal_plan_id is not None:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset

    def ensure_flags_for_plan(self, meal_plan_id: int) -> MealSettingsFlags:
        settings, _ = MealSettings.objects.get_or_create(meal_plan_id=meal_plan_id)
        enabled_meal_types = [
            meal_type
            for field, meal_type in _MEAL_TYPE_BY_ENABLED_FIELD.items()
            if getattr(settings, field)
        ]
        enabled_iso_weekdays = {
            iso_weekday
            for field, iso_weekday in _ISO_WEEKDAY_BY_DAY_FIELD.items()
            if getattr(settings, field)
        }
        return MealSettingsFlags(
            enabled_meal_types=enabled_meal_types,
            enabled_iso_weekdays=enabled_iso_weekdays,
        )


class MealSuggestionRepository:
    def healthy_content_by_meal_type(self) -> dict[str, SuggestionContent]:
        content_by_meal_type: dict[str, SuggestionContent] = {}
        for suggestion in MealSuggestion.objects.filter(is_healthy=True).prefetch_related("foods"):
            if suggestion.meal_type in content_by_meal_type:
                continue
            content_by_meal_type[suggestion.meal_type] = SuggestionContent(
                food_ids=[food.id for food in suggestion.foods.all()],
                notes=suggestion.description,
            )
        return content_by_meal_type
