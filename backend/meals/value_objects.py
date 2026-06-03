from __future__ import annotations

from dataclasses import dataclass
from datetime import date as date_type


@dataclass(frozen=True)
class FoodData:
    id: int
    name: str
    category: str


@dataclass(frozen=True)
class DailyMealData:
    id: int
    meal_plan_id: int
    date: date_type
    day_of_week: int
    meal_type: str
    foods: list[FoodData]
    notes: str


@dataclass(frozen=True)
class MealSettingsFlags:
    enabled_meal_types: list[str]
    enabled_iso_weekdays: set[int]


@dataclass(frozen=True)
class SuggestionContent:
    food_ids: list[int]
    notes: str
