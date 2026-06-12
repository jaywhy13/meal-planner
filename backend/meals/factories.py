from __future__ import annotations

import datetime

import factory
from django.contrib.auth.models import User

from .models import (
    DailyMeal,
    Food,
    Meal,
    MealPlan,
    MealSettings,
    MealSuggestion,
    MealType,
)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}@example.com")
    email = factory.LazyAttribute(lambda user: user.username)


class FoodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Food
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Food {n}")
    category = "Other"


class MealPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealPlan

    name = factory.Sequence(lambda n: f"Plan {n}")
    start_date = datetime.date(2026, 5, 1)
    user = factory.SubFactory(UserFactory)


class MealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meal

    name = factory.Sequence(lambda n: f"Meal {n}")
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def foods(self, create: bool, extracted, **kwargs) -> None:
        if create and extracted:
            self.foods.set(extracted)


class DailyMealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DailyMeal

    meal_plan = factory.SubFactory(MealPlanFactory)
    date = datetime.date(2026, 5, 4)
    meal_type = MealType.BREAKFAST


class MealSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealSettings

    meal_plan = factory.SubFactory(MealPlanFactory)


class MealSuggestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MealSuggestion

    name = factory.Sequence(lambda n: f"Suggestion {n}")
    meal_type = MealType.BREAKFAST
    is_healthy = True

    @factory.post_generation
    def foods(self, create: bool, extracted, **kwargs) -> None:
        if create and extracted:
            self.foods.set(extracted)
