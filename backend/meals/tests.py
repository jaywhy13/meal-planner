import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .factories import (
    DailyMealFactory,
    FoodFactory,
    MealFactory,
    MealPlanFactory,
    MealSettingsFactory,
    MealSuggestionFactory,
    UserFactory,
)
from .models import DailyMeal, Food, Meal, MealPlan, MealSettings, MealSuggestion, MealType
from .serializers import DailyMealSerializer


class GenerateMealPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.plan = MealPlan.objects.create(name="Test Plan", start_date="2026-05-01", user=self.user)

    def _generate_url(self):
        return reverse("mealplan-generate-meal-plan", args=[self.plan.pk])

    def test_generates_meals_for_full_month(self):
        """All 31 days of May 2026 × 4 meal types = 124 DailyMeal records"""
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        count = DailyMeal.objects.filter(meal_plan=self.plan).count()
        self.assertEqual(count, 124)  # 31 days × 4 meal types

    def test_disabled_weekend_skips_weekend_meals(self):
        """No DailyMeal should have day_of_week 6 or 7 when weekends are disabled"""
        MealSettings.objects.create(
            meal_plan=self.plan,
            saturday_enabled=False,
            sunday_enabled=False,
        )
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        weekend_meals = DailyMeal.objects.filter(meal_plan=self.plan, day_of_week__in=[6, 7])
        self.assertEqual(weekend_meals.count(), 0)

    def test_disabled_breakfast_skips_breakfast(self):
        """No DailyMeal should have meal_type='breakfast' when breakfast is disabled"""
        MealSettings.objects.create(meal_plan=self.plan, breakfast_enabled=False)
        response = self.client.post(self._generate_url(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        breakfast_meals = DailyMeal.objects.filter(meal_plan=self.plan, meal_type="breakfast")
        self.assertEqual(breakfast_meals.count(), 0)

    def test_wipe_true_deletes_existing_meals(self):
        """wipe=True should delete pre-existing meals before generating fresh ones"""
        pre_existing = DailyMeal.objects.create(
            meal_plan=self.plan,
            date=datetime.date(2026, 5, 1),
            meal_type=MealType.BREAKFAST,
        )
        pre_pk = pre_existing.pk
        response = self.client.post(self._generate_url(), {"wipe": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(DailyMeal.objects.filter(pk=pre_pk).exists())
        self.assertTrue(DailyMeal.objects.filter(meal_plan=self.plan).exists())

    def test_wipe_false_preserves_existing_meals(self):
        """wipe=False (default) should leave the pre-existing meal untouched"""
        pre_existing = DailyMeal.objects.create(
            meal_plan=self.plan,
            date=datetime.date(2026, 5, 1),
            meal_type=MealType.BREAKFAST,
        )
        pre_pk = pre_existing.pk
        response = self.client.post(self._generate_url(), {"wipe": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(DailyMeal.objects.filter(pk=pre_pk).exists())


class MealSettingsDayToggleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def _create_plan_and_settings(self):
        plan = MealPlan.objects.create(name="Plan", start_date="2026-05-01", user=self.user)
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
        MealPlan.objects.create(name="Plan A", start_date="2026-05-01", user=self.user)
        url = reverse("mealplan-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("start_date", response.data[0])

    def test_start_date_in_detail_response(self):
        plan = MealPlan.objects.create(name="Plan A", start_date="2026-05-01", user=self.user)
        url = reverse("mealplan-detail", args=[plan.pk])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_date"], "2026-05-01")


class DailyMealModelTest(APITestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(name="Test Plan", start_date="2026-05-01")

    def test_monday_sets_day_of_week_1(self):
        meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan,
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.BREAKFAST,
        )
        self.assertEqual(meal.day_of_week, 1)

    def test_sunday_sets_day_of_week_7(self):
        meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan,
            date=datetime.date(2026, 5, 10),
            meal_type=MealType.LUNCH,
        )
        self.assertEqual(meal.day_of_week, 7)

    def test_duplicate_meal_plan_date_meal_type_raises_integrity_error(self):
        DailyMeal.objects.create(
            meal_plan=self.meal_plan,
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.DINNER,
        )
        with self.assertRaises(IntegrityError):
            DailyMeal.objects.create(
                meal_plan=self.meal_plan,
                date=datetime.date(2026, 5, 4),
                meal_type=MealType.DINNER,
            )


class DailyMealSerializerTest(APITestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(name="Serializer Plan", start_date="2026-05-01")
        self.daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan,
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.BREAKFAST,
        )

    def test_serializer_exposes_date(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertIn("date", serializer.data)
        self.assertEqual(serializer.data["date"], "2026-05-04")

    def test_serializer_exposes_day_of_week(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertIn("day_of_week", serializer.data)
        self.assertEqual(serializer.data["day_of_week"], 1)

    def test_serializer_does_not_expose_week(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertNotIn("week", serializer.data)

    def test_serializer_does_not_expose_day(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertNotIn("day", serializer.data)


class MealCrudTests(APITestCase):
    def test_create_meal_assigns_requesting_user_as_owner(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        avocado = FoodFactory(name="Avocado")
        url = reverse("meal-list")
        response = self.client.post(
            url,
            {"name": "Avocado Toast", "food_ids": [avocado.id], "notes": "Quick breakfast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_meal = Meal.objects.get(id=response.data["id"])
        self.assertEqual(created_meal.user, requesting_user)

    def test_create_meal_persists_foods_and_notes(self):
        self.client.force_authenticate(user=UserFactory())
        avocado = FoodFactory(name="Avocado")
        toast = FoodFactory(name="Toast")
        url = reverse("meal-list")
        response = self.client.post(
            url,
            {"name": "Avocado Toast", "food_ids": [avocado.id, toast.id], "notes": "Quick breakfast"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_meal = Meal.objects.get(id=response.data["id"])
        self.assertEqual(created_meal.notes, "Quick breakfast")
        for expected_food_id in [avocado.id, toast.id]:
            self.assertTrue(created_meal.foods.filter(id=expected_food_id).exists())

    def test_list_returns_only_meals_owned_by_requesting_user(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        own_meal = MealFactory(user=requesting_user, name="My Meal")
        MealFactory(user=UserFactory(), name="Their Meal")
        url = reverse("meal-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [meal["id"] for meal in response.data]
        self.assertEqual(returned_ids, [own_meal.id])

    def test_search_filters_meals_by_name(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        MealFactory(user=requesting_user, name="Avocado Toast")
        MealFactory(user=requesting_user, name="Chicken Salad")
        url = reverse("meal-list")
        response = self.client.get(url, {"search": "avocado"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_names = [meal["name"] for meal in response.data]
        self.assertEqual(returned_names, ["Avocado Toast"])

    def test_update_meal_replaces_foods(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        original_food = FoodFactory(name="Eggs")
        replacement_food = FoodFactory(name="Oats")
        meal = MealFactory(user=requesting_user, name="Breakfast", foods=[original_food])
        url = reverse("meal-detail", args=[meal.id])
        response = self.client.patch(url, {"food_ids": [replacement_food.id]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meal.refresh_from_db()
        self.assertFalse(meal.foods.filter(id=original_food.id).exists())
        self.assertTrue(meal.foods.filter(id=replacement_food.id).exists())

    def test_delete_meal_removes_it(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        meal = MealFactory(user=requesting_user, name="Disposable")
        url = reverse("meal-detail", args=[meal.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Meal.objects.filter(id=meal.id).exists())


class DailyMealMealLinkTests(APITestCase):
    def test_serializer_nests_meal_with_primary_key(self):
        owner = UserFactory()
        avocado = FoodFactory(name="Avocado")
        meal = MealFactory(user=owner, name="Avocado Toast", notes="Tasty", foods=[avocado])
        daily_meal = DailyMealFactory(
            meal_plan=MealPlanFactory(user=owner),
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.BREAKFAST,
            meal=meal,
        )
        serializer = DailyMealSerializer(daily_meal)
        self.assertEqual(serializer.data["meal"]["id"], meal.id)
        self.assertEqual(serializer.data["meal"]["name"], "Avocado Toast")
        self.assertEqual(serializer.data["meal"]["foods"][0]["name"], "Avocado")

    def test_create_daily_meal_accepts_meal_id(self):
        owner = UserFactory()
        self.client.force_authenticate(user=owner)
        meal = MealFactory(user=owner, name="Lunch")
        plan = MealPlanFactory(user=owner)
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {
                "meal_plan": plan.id,
                "date": "2026-05-04",
                "meal_type": MealType.LUNCH,
                "meal_id": meal.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_daily_meal = DailyMeal.objects.get(id=response.data["id"])
        self.assertEqual(created_daily_meal.meal, meal)

    def test_daily_meal_write_via_meal_id_exposes_foods_through_meal(self):
        """The frontend write path attaches a Meal carrying foods; those foods must
        be reachable through daily_meal.meal.foods after the slot is created."""
        owner = UserFactory()
        self.client.force_authenticate(user=owner)
        avocado = FoodFactory(name="Avocado")
        toast = FoodFactory(name="Toast")
        meal = MealFactory(user=owner, name="Avocado Toast", foods=[avocado, toast])
        plan = MealPlanFactory(user=owner)
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {
                "meal_plan": plan.id,
                "date": "2026-05-04",
                "meal_type": MealType.BREAKFAST,
                "meal_id": meal.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_daily_meal = DailyMeal.objects.get(id=response.data["id"])
        for expected_food_id in [avocado.id, toast.id]:
            self.assertTrue(created_daily_meal.meal.foods.filter(id=expected_food_id).exists())

    def test_meal_daily_meals_returns_every_slot_using_it(self):
        owner = UserFactory()
        meal = MealFactory(user=owner, name="Reused")
        plan = MealPlanFactory(user=owner)
        breakfast_slot = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST, meal=meal
        )
        lunch_slot = DailyMealFactory(
            meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.LUNCH, meal=meal
        )
        linked_slot_ids = set(meal.daily_meals.values_list("id", flat=True))
        self.assertEqual(linked_slot_ids, {breakfast_slot.id, lunch_slot.id})

    def test_deleting_meal_empties_slot_without_deleting_it(self):
        owner = UserFactory()
        meal = MealFactory(user=owner, name="Doomed")
        slot = DailyMealFactory(
            meal_plan=MealPlanFactory(user=owner),
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.DINNER,
            meal=meal,
        )
        meal.delete()
        slot.refresh_from_db()
        self.assertIsNone(slot.meal)


class DailyMealMealOwnershipTests(APITestCase):
    def test_create_with_another_users_meal_is_rejected(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        other_users_meal = MealFactory(user=UserFactory(), name="Not Yours")
        plan = MealPlanFactory(user=requesting_user)
        url = reverse("dailymeal-list")
        response = self.client.post(
            url,
            {
                "meal_plan": plan.id,
                "date": "2026-05-04",
                "meal_type": MealType.LUNCH,
                "meal_id": other_users_meal.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_attaching_another_users_meal_is_rejected_and_slot_unchanged(self):
        requesting_user = UserFactory()
        self.client.force_authenticate(user=requesting_user)
        own_meal = MealFactory(user=requesting_user, name="Mine")
        other_users_meal = MealFactory(user=UserFactory(), name="Not Yours")
        slot = DailyMealFactory(
            meal_plan=MealPlanFactory(user=requesting_user),
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.DINNER,
            meal=own_meal,
        )
        url = reverse("dailymeal-detail", args=[slot.id])
        response = self.client.patch(url, {"meal_id": other_users_meal.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        slot.refresh_from_db()
        self.assertEqual(slot.meal, own_meal)


class GenerateMealPlanMealReuseTests(APITestCase):
    def _generate_url(self, plan):
        return reverse("mealplan-generate-meal-plan", args=[plan.pk])

    def test_one_meal_created_per_suggestion_then_reused_across_slots(self):
        owner = UserFactory()
        self.client.force_authenticate(user=owner)
        MealSuggestionFactory(
            name="Avocado Toast",
            meal_type=MealType.BREAKFAST,
            description="Tasty",
            foods=[FoodFactory(name="Avocado")],
        )
        plan = MealPlanFactory(user=owner)
        MealSettingsFactory(
            meal_plan=plan,
            lunch_enabled=False,
            dinner_enabled=False,
            snack_enabled=False,
        )
        response = self.client.post(self._generate_url(plan), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meals_named_after_suggestion = Meal.objects.filter(user=owner, name="Avocado Toast")
        self.assertEqual(meals_named_after_suggestion.count(), 1)

    def test_reused_meal_is_linked_to_every_generated_breakfast_slot(self):
        owner = UserFactory()
        self.client.force_authenticate(user=owner)
        MealSuggestionFactory(
            name="Avocado Toast",
            meal_type=MealType.BREAKFAST,
            description="Tasty",
            foods=[FoodFactory(name="Avocado")],
        )
        plan = MealPlanFactory(user=owner)
        MealSettingsFactory(
            meal_plan=plan,
            lunch_enabled=False,
            dinner_enabled=False,
            snack_enabled=False,
        )
        self.client.post(self._generate_url(plan), {}, format="json")
        reused_meal = Meal.objects.get(user=owner, name="Avocado Toast")
        breakfast_slots = DailyMeal.objects.filter(meal_plan=plan, meal_type=MealType.BREAKFAST)
        for breakfast_slot in breakfast_slots:
            self.assertEqual(breakfast_slot.meal, reused_meal)

    def test_generated_meal_is_owned_by_plan_owner(self):
        owner = UserFactory()
        self.client.force_authenticate(user=owner)
        MealSuggestionFactory(
            name="Avocado Toast",
            meal_type=MealType.BREAKFAST,
            description="Tasty",
            foods=[FoodFactory(name="Avocado")],
        )
        plan = MealPlanFactory(user=owner)
        self.client.post(self._generate_url(plan), {}, format="json")
        reused_meal = Meal.objects.get(name="Avocado Toast")
        self.assertEqual(reused_meal.user, owner)


class ExtractMealMigrationTests(TransactionTestCase):
    migrate_from = ("meals", "0006_dailymeal_date_day_of_week")
    migrate_to = ("meals", "0009_remove_daily_meal_foods_notes")

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        executor.loader.build_graph()
        return executor.loader.project_state(targets).apps

    def test_non_empty_daily_meal_becomes_linked_meal_carrying_foods_and_notes(self):
        old_apps = self._migrate([self.migrate_from])
        OldUser = old_apps.get_model("auth", "User")
        OldFood = old_apps.get_model("meals", "Food")
        OldMealPlan = old_apps.get_model("meals", "MealPlan")
        OldDailyMeal = old_apps.get_model("meals", "DailyMeal")

        owner = OldUser.objects.create(username="historical@example.com")
        avocado = OldFood.objects.create(name="Avocado")
        plan = OldMealPlan.objects.create(name="Plan", start_date="2026-05-01", user=owner)
        daily_meal = OldDailyMeal.objects.create(
            meal_plan=plan,
            date=datetime.date(2026, 5, 4),
            day_of_week=1,
            meal_type="breakfast",
            notes="Tasty",
        )
        daily_meal.foods.set([avocado])

        new_apps = self._migrate([self.migrate_to])
        MigratedDailyMeal = new_apps.get_model("meals", "DailyMeal")

        migrated_daily_meal = MigratedDailyMeal.objects.get(id=daily_meal.id)
        linked_meal = migrated_daily_meal.meal
        self.assertIsNotNone(linked_meal)
        self.assertEqual(linked_meal.notes, "Tasty")
        self.assertEqual(linked_meal.user_id, owner.id)
        self.assertTrue(linked_meal.foods.filter(id=avocado.id).exists())

    def test_apply_reverse_reapply_leaves_exactly_one_meal_per_non_empty_slot(self):
        old_apps = self._migrate([self.migrate_from])
        OldUser = old_apps.get_model("auth", "User")
        OldFood = old_apps.get_model("meals", "Food")
        OldMealPlan = old_apps.get_model("meals", "MealPlan")
        OldDailyMeal = old_apps.get_model("meals", "DailyMeal")

        owner = OldUser.objects.create(username="replay@example.com")
        avocado = OldFood.objects.create(name="Avocado")
        plan = OldMealPlan.objects.create(name="Plan", start_date="2026-05-01", user=owner)
        daily_meal = OldDailyMeal.objects.create(
            meal_plan=plan,
            date=datetime.date(2026, 5, 4),
            day_of_week=1,
            meal_type="breakfast",
            notes="Tasty",
        )
        daily_meal.foods.set([avocado])

        self._migrate([self.migrate_to])
        self._migrate([("meals", "0006_dailymeal_date_day_of_week")])
        replayed_apps = self._migrate([self.migrate_to])

        ReplayedDailyMeal = replayed_apps.get_model("meals", "DailyMeal")
        ReplayedMeal = replayed_apps.get_model("meals", "Meal")
        self.assertEqual(ReplayedMeal.objects.count(), 1)
        replayed_daily_meal = ReplayedDailyMeal.objects.get(id=daily_meal.id)
        self.assertEqual(replayed_daily_meal.meal.notes, "Tasty")
        self.assertTrue(replayed_daily_meal.meal.foods.filter(id=avocado.id).exists())

    def test_empty_daily_meal_is_left_unlinked(self):
        old_apps = self._migrate([self.migrate_from])
        OldMealPlan = old_apps.get_model("meals", "MealPlan")
        OldDailyMeal = old_apps.get_model("meals", "DailyMeal")

        plan = OldMealPlan.objects.create(name="Plan", start_date="2026-05-01")
        empty_daily_meal = OldDailyMeal.objects.create(
            meal_plan=plan,
            date=datetime.date(2026, 5, 4),
            day_of_week=1,
            meal_type="lunch",
        )

        new_apps = self._migrate([self.migrate_to])
        MigratedDailyMeal = new_apps.get_model("meals", "DailyMeal")
        MigratedMeal = new_apps.get_model("meals", "Meal")

        migrated_daily_meal = MigratedDailyMeal.objects.get(id=empty_daily_meal.id)
        self.assertIsNone(migrated_daily_meal.meal)
        self.assertEqual(MigratedMeal.objects.count(), 0)

    def tearDown(self):
        self._migrate([self.migrate_to])
