from __future__ import annotations

import datetime

import factory
from django.contrib.auth.models import User

from .models import DailyMeal, Food, Meal, MealPlan, MealSettings, MealSuggestion, MealType


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda index: f"user{index}@example.com")
    email = factory.LazyAttribute(lambda user: user.username)


class FoodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Food

    name = factory.Sequence(lambda index: f"Food {index}")
    category = ""


class MealPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealPlan

    name = factory.Sequence(lambda index: f"Plan {index}")
    start_date = datetime.date(2026, 5, 1)
    user = factory.SubFactory(UserFactory)


class MealSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealSettings

    meal_plan = factory.SubFactory(MealPlanFactory)


class MealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meal
        skip_postgeneration_save = True

    name = factory.Sequence(lambda index: f"Meal {index}")
    notes = ""
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def foods(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.foods.set(extracted)


class MealSuggestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealSuggestion
        skip_postgeneration_save = True

    name = factory.Sequence(lambda index: f"Suggestion {index}")
    description = ""
    meal_type = MealType.BREAKFAST
    is_healthy = True

    @factory.post_generation
    def foods(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.foods.set(extracted)


class DailyMealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DailyMeal

    meal_plan = factory.SubFactory(MealPlanFactory)
    date = datetime.date(2026, 5, 4)
    meal_type = MealType.BREAKFAST
    meal = None
