import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from meals.factories import (
    DailyMealFactory,
    FoodFactory,
    MealFactory,
    MealPlanFactory,
    MealSettingsFactory,
    UserFactory,
)
from meals.models import DailyMeal, MealType


class DailyMealMealLinkTests(APITestCase):
    def test_deleting_meal_empties_daily_meal(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal = MealFactory(user=user, name="Lunch")
        plan = MealPlanFactory(user=user)
        daily_meal = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH, meal=meal
        )

        meal.delete()

        daily_meal.refresh_from_db()
        self.assertIsNone(daily_meal.meal)

    def test_meal_daily_meals_reverse_relation_lists_all_daily_meals(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal = MealFactory(user=user, name="Lunch")
        plan = MealPlanFactory(user=user)
        first_daily_meal = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH, meal=meal
        )
        second_daily_meal = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 5), meal_type=MealType.DINNER, meal=meal
        )

        linked_daily_meal_ids = set(meal.daily_meals.values_list("id", flat=True))

        self.assertEqual(linked_daily_meal_ids, {first_daily_meal.id, second_daily_meal.id})

    def test_daily_meal_serializes_nested_meal_with_pk(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        eggs = FoodFactory(name="Eggs")
        meal = MealFactory(user=user, name="Breakfast", foods=[eggs])
        plan = MealPlanFactory(user=user)
        DailyMealFactory(meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST, meal=meal)
        daily_meal_list_url = reverse("dailymeal-list")

        response = self.client.get(daily_meal_list_url, {"meal_plan": plan.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nested_meal = response.data[0]["meal"]
        self.assertEqual(nested_meal["id"], meal.id)
        self.assertEqual(nested_meal["foods"][0]["name"], "Eggs")

    def test_create_daily_meal_with_meal_id(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal = MealFactory(user=user, name="Dinner")
        plan = MealPlanFactory(user=user)
        daily_meal_list_url = reverse("dailymeal-list")

        response = self.client.post(
            daily_meal_list_url,
            {
                "meal_plan": plan.id,
                "date": "2026-05-04",
                "meal_type": MealType.DINNER,
                "meal_id": meal.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_daily_meal = DailyMeal.objects.get(pk=response.data["id"])
        self.assertEqual(created_daily_meal.meal, meal)


class MealSettingsDayToggleTests(APITestCase):
    def test_day_toggles_in_api_response(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user)
        settings = MealSettingsFactory(meal_plan=plan)
        url = reverse("mealsettings-detail", args=[settings.pk])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in [
            "monday_enabled",
            "tuesday_enabled",
            "wednesday_enabled",
            "thursday_enabled",
            "friday_enabled",
            "saturday_enabled",
            "sunday_enabled",
        ]:
            self.assertIn(field, response.data)
            self.assertTrue(response.data[field])

    def test_patch_day_toggles(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        settings = MealSettingsFactory(meal_plan=MealPlanFactory(user=user))
        url = reverse("mealsettings-detail", args=[settings.pk])

        response = self.client.patch(url, {"saturday_enabled": False, "sunday_enabled": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["saturday_enabled"])
        self.assertFalse(response.data["sunday_enabled"])
        self.assertTrue(response.data["monday_enabled"])

    def test_patch_day_toggle_persists(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        settings = MealSettingsFactory(meal_plan=MealPlanFactory(user=user))
        url = reverse("mealsettings-detail", args=[settings.pk])

        self.client.patch(url, {"saturday_enabled": False}, format="json")

        settings.refresh_from_db()
        self.assertFalse(settings.saturday_enabled)


class MealPlanStartDateTests(APITestCase):
    def test_create_without_start_date_returns_400(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("mealplan-list")

        response = self.client.post(url, {"name": "Test Plan"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_date", response.data)

    def test_create_with_start_date_succeeds(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("mealplan-list")

        response = self.client.post(url, {"name": "Test Plan", "start_date": "2026-05-01"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["start_date"], "2026-05-01")

    def test_start_date_in_list_response(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        MealPlanFactory(user=user, name="Plan A", start_date=datetime.date(2026, 5, 1))
        url = reverse("mealplan-list")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("start_date", response.data[0])

    def test_start_date_in_detail_response(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        plan = MealPlanFactory(user=user, name="Plan A", start_date=datetime.date(2026, 5, 1))
        url = reverse("mealplan-detail", args=[plan.pk])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_date"], "2026-05-01")
