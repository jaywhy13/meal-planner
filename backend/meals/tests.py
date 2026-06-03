import calendar
import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DailyMeal, Food, Meal, MealPlan, MealSettings, MealSuggestion, MealType

PLAN_START_DATE = datetime.date(2026, 5, 1)
DAYS_IN_PLAN_MONTH = calendar.monthrange(PLAN_START_DATE.year, PLAN_START_DATE.month)[1]
MEAL_TYPE_COUNT = len(MealType.choices)


class GenerateMealPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.plan = MealPlan.objects.create(name="Test Plan", start_date=PLAN_START_DATE, user=self.user)

    def _generate_url(self):
        return reverse("mealplan-generate-meal-plan", args=[self.plan.pk])

    def test_generates_a_slot_for_each_enabled_day_and_meal_type(self):
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        daily_meal_count = DailyMeal.objects.filter(meal_plan=self.plan).count()
        self.assertEqual(daily_meal_count, DAYS_IN_PLAN_MONTH * MEAL_TYPE_COUNT)

    def test_generates_each_meal_type_on_each_day(self):
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for meal_type, _ in MealType.choices:
            slots_for_type = DailyMeal.objects.filter(meal_plan=self.plan, meal_type=meal_type).count()
            self.assertEqual(slots_for_type, DAYS_IN_PLAN_MONTH)

    def test_disabled_weekend_skips_weekend_slots(self):
        MealSettings.objects.create(
            meal_plan=self.plan,
            saturday_enabled=False,
            sunday_enabled=False,
        )
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        weekend_slots = DailyMeal.objects.filter(meal_plan=self.plan, day_of_week__in=[6, 7])
        self.assertEqual(weekend_slots.count(), 0)

    def test_disabled_breakfast_skips_breakfast_slots(self):
        MealSettings.objects.create(meal_plan=self.plan, breakfast_enabled=False)
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        breakfast_slots = DailyMeal.objects.filter(meal_plan=self.plan, meal_type="breakfast")
        self.assertEqual(breakfast_slots.count(), 0)

    def test_generation_assigns_suggestion_foods_to_slots(self):
        oatmeal = Food.objects.create(name="Oatmeal")
        suggestion = MealSuggestion.objects.create(name="Oats", meal_type="breakfast", description="Hearty")
        suggestion.foods.set([oatmeal])
        self.client.post(self._generate_url(), {}, format="json")
        breakfast_slot = DailyMeal.objects.filter(meal_plan=self.plan, meal_type="breakfast").first()
        self.assertIsNotNone(breakfast_slot.meal)
        self.assertIn(oatmeal, breakfast_slot.meal.foods.all())

    def test_wipe_true_deletes_existing_slots(self):
        existing_slot = DailyMeal.objects.create(
            meal_plan=self.plan, date=datetime.date(2026, 5, 1), meal_type=MealType.BREAKFAST
        )
        response = self.client.post(self._generate_url(), {"wipe": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(DailyMeal.objects.filter(pk=existing_slot.pk).exists())
        self.assertTrue(DailyMeal.objects.filter(meal_plan=self.plan).exists())

    def test_wipe_false_preserves_existing_slots(self):
        existing_slot = DailyMeal.objects.create(
            meal_plan=self.plan, date=datetime.date(2026, 5, 1), meal_type=MealType.BREAKFAST
        )
        response = self.client.post(self._generate_url(), {"wipe": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(DailyMeal.objects.filter(pk=existing_slot.pk).exists())


class MealSettingsDayToggleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def _create_plan_and_settings(self):
        plan = MealPlan.objects.create(name="Plan", start_date=PLAN_START_DATE, user=self.user)
        settings = MealSettings.objects.create(meal_plan=plan)
        return plan, settings

    def test_new_settings_default_all_days_true(self):
        _, settings = self._create_plan_and_settings()
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            self.assertTrue(getattr(settings, f"{day}_enabled"), f"{day}_enabled should default to True")

    def test_day_toggles_in_api_response(self):
        _, settings = self._create_plan_and_settings()
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
        _, settings = self._create_plan_and_settings()
        url = reverse("mealsettings-detail", args=[settings.pk])
        response = self.client.patch(
            url,
            {"saturday_enabled": False, "sunday_enabled": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["saturday_enabled"])
        self.assertFalse(response.data["sunday_enabled"])
        self.assertTrue(response.data["monday_enabled"])

    def test_patch_day_toggle_persists(self):
        _, settings = self._create_plan_and_settings()
        url = reverse("mealsettings-detail", args=[settings.pk])
        self.client.patch(url, {"saturday_enabled": False}, format="json")
        settings.refresh_from_db()
        self.assertFalse(settings.saturday_enabled)


class MealPlanStartDateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="startdate@example.com",
            email="startdate@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_without_start_date_returns_400(self):
        url = reverse("mealplan-list")
        response = self.client.post(url, {"name": "Test Plan"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_date", response.data)

    def test_create_with_start_date_succeeds(self):
        url = reverse("mealplan-list")
        response = self.client.post(url, {"name": "Test Plan", "start_date": "2026-05-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["start_date"], "2026-05-01")

    def test_start_date_in_list_response(self):
        MealPlan.objects.create(name="Plan A", start_date=PLAN_START_DATE, user=self.user)
        url = reverse("mealplan-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("start_date", response.data[0])

    def test_start_date_in_detail_response(self):
        plan = MealPlan.objects.create(name="Plan A", start_date=PLAN_START_DATE, user=self.user)
        url = reverse("mealplan-detail", args=[plan.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_date"], "2026-05-01")


class DailyMealModelTest(APITestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(name="Test Plan", start_date=PLAN_START_DATE)

    def test_monday_sets_day_of_week_1(self):
        daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        self.assertEqual(daily_meal.day_of_week, 1)

    def test_sunday_sets_day_of_week_7(self):
        daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 10), meal_type=MealType.BREAKFAST
        )
        self.assertEqual(daily_meal.day_of_week, 7)

    def test_same_plan_date_and_meal_type_raises_integrity_error(self):
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        with self.assertRaises(IntegrityError):
            DailyMeal.objects.create(
                meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
            )

    def test_different_meal_types_on_same_day_coexist(self):
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH
        )
        slots_on_day = DailyMeal.objects.filter(meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4))
        self.assertEqual(slots_on_day.count(), 2)


class MealModelTest(APITestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(name="Test Plan", start_date=PLAN_START_DATE)

    def test_meal_carries_foods_and_notes(self):
        oatmeal = Food.objects.create(name="Oatmeal")
        meal = Meal.objects.create(notes="With berries")
        meal.foods.set([oatmeal])
        self.assertEqual(meal.notes, "With berries")
        self.assertIn(oatmeal, meal.foods.all())

    def test_daily_meal_links_one_meal(self):
        meal = Meal.objects.create(notes="Shared")
        daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST, meal=meal
        )
        self.assertEqual(daily_meal.meal, meal)

    def test_one_meal_can_belong_to_many_daily_meals(self):
        reusable_meal = Meal.objects.create(notes="Leftovers")
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH, meal=reusable_meal
        )
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 5), meal_type=MealType.DINNER, meal=reusable_meal
        )
        self.assertEqual(reusable_meal.daily_meals.count(), 2)


class DailyMealApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mealapi@example.com",
            email="mealapi@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.meal_plan = MealPlan.objects.create(name="Api Plan", start_date=PLAN_START_DATE, user=self.user)

    def test_create_daily_meal_sets_day_of_week(self):
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {"meal_plan": self.meal_plan.pk, "date": "2026-05-04", "meal_type": "breakfast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["day_of_week"], 1)
        daily_meal = DailyMeal.objects.get(meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4))
        self.assertEqual(daily_meal.meal_type, "breakfast")

    def test_create_daily_meal_links_foods(self):
        eggs = Food.objects.create(name="Eggs")
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {
                "meal_plan": self.meal_plan.pk,
                "date": "2026-05-04",
                "meal_type": "breakfast",
                "food_ids": [eggs.pk],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        daily_meal = DailyMeal.objects.get(pk=response.data["id"])
        self.assertIn(eggs, daily_meal.meal.foods.all())

    def test_create_daily_meal_on_unowned_plan_is_forbidden(self):
        other_user = User.objects.create_user(username="intruder@example.com", password="x")
        plan_for_other_user = MealPlan.objects.create(
            name="Other", start_date=PLAN_START_DATE, user=other_user
        )
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {"meal_plan": plan_for_other_user.pk, "date": "2026-05-04", "meal_type": "breakfast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_daily_meal_replaces_foods_and_notes(self):
        daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        toast = Food.objects.create(name="Toast")
        url = reverse("dailymeal-detail", args=[daily_meal.pk])
        response = self.client.put(
            url,
            {
                "meal_plan": self.meal_plan.pk,
                "date": "2026-05-04",
                "meal_type": "breakfast",
                "food_ids": [toast.pk],
                "notes": "Buttered",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        daily_meal.refresh_from_db()
        self.assertEqual(daily_meal.meal.notes, "Buttered")
        self.assertIn(toast, daily_meal.meal.foods.all())

    def test_delete_daily_meal(self):
        daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        url = reverse("dailymeal-detail", args=[daily_meal.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(DailyMeal.objects.filter(pk=daily_meal.pk).exists())

    def test_list_daily_meals_filtered_by_meal_plan(self):
        daily_meal_for_breakfast = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        plan_for_another_month = MealPlan.objects.create(
            name="Other", start_date=datetime.date(2026, 6, 1), user=self.user
        )
        DailyMeal.objects.create(
            meal_plan=plan_for_another_month, date=datetime.date(2026, 6, 4), meal_type=MealType.LUNCH
        )

        url = reverse("dailymeal-list")
        response = self.client.get(url, {"meal_plan": self.meal_plan.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], daily_meal_for_breakfast.pk)
        self.assertEqual(response.data[0]["meal_type"], "breakfast")

    def test_list_daily_meals_excludes_other_users(self):
        other_user = User.objects.create_user(username="other@example.com", password="x")
        plan_for_other_user = MealPlan.objects.create(
            name="Other", start_date=PLAN_START_DATE, user=other_user
        )
        DailyMeal.objects.create(
            meal_plan=plan_for_other_user, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH
        )

        url = reverse("dailymeal-list")
        response = self.client.get(url, {"meal_plan": plan_for_other_user.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_non_numeric_pk_returns_404(self):
        response = self.client.get("/api/daily-meals/abc", format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_numeric_pk_returns_404(self):
        response = self.client.delete("/api/daily-meals/abc")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_missing_daily_meal_returns_404(self):
        url = reverse("dailymeal-detail", args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_daily_meal_owned_by_another_user_returns_404(self):
        other_user = User.objects.create_user(username="stranger@example.com", password="x")
        plan_for_other_user = MealPlan.objects.create(
            name="Other", start_date=PLAN_START_DATE, user=other_user
        )
        daily_meal_of_other_user = DailyMeal.objects.create(
            meal_plan=plan_for_other_user, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH
        )
        url = reverse("dailymeal-detail", args=[daily_meal_of_other_user.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(DailyMeal.objects.filter(pk=daily_meal_of_other_user.pk).exists())

    def test_create_daily_meal_without_content_creates_no_meal(self):
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {"meal_plan": self.meal_plan.pk, "date": "2026-05-04", "meal_type": "breakfast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        daily_meal = DailyMeal.objects.get(pk=response.data["id"])
        self.assertIsNone(daily_meal.meal)
        self.assertEqual(Meal.objects.count(), 0)

    def test_update_does_not_mutate_meal_shared_with_another_slot(self):
        leftovers = Food.objects.create(name="Leftovers")
        shared_meal = Meal.objects.create(notes="Shared")
        shared_meal.foods.set([leftovers])
        lunch_slot = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH, meal=shared_meal
        )
        dinner_slot = DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.DINNER, meal=shared_meal
        )

        soup = Food.objects.create(name="Soup")
        url = reverse("dailymeal-detail", args=[lunch_slot.pk])
        response = self.client.put(
            url,
            {
                "meal_plan": self.meal_plan.pk,
                "date": "2026-05-04",
                "meal_type": "lunch",
                "food_ids": [soup.pk],
                "notes": "Tomato soup",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dinner_slot.refresh_from_db()
        self.assertEqual(dinner_slot.meal, shared_meal)
        self.assertEqual(shared_meal.notes, "Shared")
        self.assertIn(leftovers, shared_meal.foods.all())


class DailyMealResponseShapeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="shape@example.com", password="x")
        self.client.force_authenticate(user=self.user)
        self.meal_plan = MealPlan.objects.create(name="Shape Plan", start_date=PLAN_START_DATE, user=self.user)

    def test_response_exposes_date_meal_plan_and_day_of_week(self):
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        url = reverse("dailymeal-list")
        response = self.client.get(url, {"meal_plan": self.meal_plan.pk}, format="json")
        slot = response.data[0]
        self.assertEqual(slot["date"], "2026-05-04")
        self.assertEqual(slot["meal_plan"], self.meal_plan.pk)
        self.assertEqual(slot["day_of_week"], 1)

    def test_plan_detail_nests_daily_meals_with_foods(self):
        eggs = Food.objects.create(name="Eggs")
        meal = Meal.objects.create(notes="Scrambled")
        meal.foods.set([eggs])
        DailyMeal.objects.create(
            meal_plan=self.meal_plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST, meal=meal
        )
        url = reverse("mealplan-detail", args=[self.meal_plan.pk])
        response = self.client.get(url, format="json")
        nested = response.data["daily_meals"][0]
        self.assertEqual(nested["meal_type"], "breakfast")
        self.assertEqual(nested["notes"], "Scrambled")
        self.assertEqual(nested["foods"][0]["name"], "Eggs")
