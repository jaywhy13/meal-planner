import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from meals.factories import (
    DailyMealFactory,
    FoodFactory,
    MealPlanFactory,
    MealSettingsFactory,
    MealSuggestionFactory,
    UserFactory,
)
from meals.models import DailyMeal, Meal, MealType


class GenerateMealPlanTests(APITestCase):
    def _generate_url(self, plan):
        return reverse("mealplan-generate-meal-plan", args=[plan.pk])

    def test_generates_meals_for_full_month(self):
        """All 31 days of May 2026 × 4 meal types = 124 DailyMeal records"""
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))

        response = self.client.post(self._generate_url(plan), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DailyMeal.objects.filter(meal_plan=plan).count(), 124)

    def test_disabled_weekend_skips_weekend_meals(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        MealSettingsFactory(meal_plan=plan, saturday_enabled=False, sunday_enabled=False)

        response = self.client.post(self._generate_url(plan), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        weekend_meals = DailyMeal.objects.filter(meal_plan=plan, day_of_week__in=[6, 7])
        self.assertEqual(weekend_meals.count(), 0)

    def test_disabled_breakfast_skips_breakfast(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        MealSettingsFactory(meal_plan=plan, breakfast_enabled=False)

        response = self.client.post(self._generate_url(plan), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        breakfast_meals = DailyMeal.objects.filter(meal_plan=plan, meal_type="breakfast")
        self.assertEqual(breakfast_meals.count(), 0)

    def test_wipe_true_deletes_existing_meals(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        pre_existing = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 1), meal_type=MealType.BREAKFAST
        )

        response = self.client.post(self._generate_url(plan), {"wipe": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(DailyMeal.objects.filter(pk=pre_existing.pk).exists())
        self.assertTrue(DailyMeal.objects.filter(meal_plan=plan).exists())

    def test_wipe_false_preserves_existing_meals(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        pre_existing = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 1), meal_type=MealType.BREAKFAST
        )

        response = self.client.post(self._generate_url(plan), {"wipe": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(DailyMeal.objects.filter(pk=pre_existing.pk).exists())

    def test_generation_reuses_one_meal_per_suggestion(self):
        """Every breakfast daily meal points at the single Meal built from the breakfast suggestion"""
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        oats = FoodFactory(name="Oats")
        MealSuggestionFactory(name="Oatmeal", meal_type=MealType.BREAKFAST, foods=[oats])

        self.client.post(self._generate_url(plan), {}, format="json")

        breakfast_daily_meals = DailyMeal.objects.filter(meal_plan=plan, meal_type="breakfast")
        distinct_meal_ids = set(breakfast_daily_meals.values_list("meal_id", flat=True))
        self.assertEqual(len(distinct_meal_ids), 1)
        reused_meal = Meal.objects.get(pk=distinct_meal_ids.pop())
        self.assertEqual(reused_meal.name, "Oatmeal")
        self.assertEqual(reused_meal.user, user)

    def test_generated_meal_carries_suggestion_foods_and_notes(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, start_date=datetime.date(2026, 5, 1))
        oats = FoodFactory(name="Oats")
        MealSuggestionFactory(
            name="Oatmeal",
            description="Warm oats",
            meal_type=MealType.BREAKFAST,
            foods=[oats],
        )

        self.client.post(self._generate_url(plan), {}, format="json")

        generated_meal = Meal.objects.get(name="Oatmeal")
        self.assertEqual(generated_meal.notes, "Warm oats")
        self.assertIn(oats, generated_meal.foods.all())
