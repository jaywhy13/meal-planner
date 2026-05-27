import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DailyMeal, MealPlan, MealSettings, MealType
from .serializers import DailyMealSerializer


class GenerateMealPlanTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)
        self.plan = MealPlan.objects.create(name='Test Plan', start_date='2026-05-01', user=self.user)

    def _generate_url(self):
        return reverse('mealplan-generate-meal-plan', args=[self.plan.pk])

    def test_generates_meals_for_full_month(self):
        """All 31 days of May 2026 × 4 meal types = 124 DailyMeal records"""
        response = self.client.post(self._generate_url(), {}, format='json')
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
        response = self.client.post(self._generate_url(), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        weekend_meals = DailyMeal.objects.filter(
            meal_plan=self.plan, day_of_week__in=[6, 7]
        )
        self.assertEqual(weekend_meals.count(), 0)

    def test_disabled_breakfast_skips_breakfast(self):
        """No DailyMeal should have meal_type='breakfast' when breakfast is disabled"""
        MealSettings.objects.create(meal_plan=self.plan, breakfast_enabled=False)
        response = self.client.post(self._generate_url(), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        breakfast_meals = DailyMeal.objects.filter(
            meal_plan=self.plan, meal_type='breakfast'
        )
        self.assertEqual(breakfast_meals.count(), 0)

    def test_wipe_true_deletes_existing_meals(self):
        """wipe=True should delete pre-existing meals before generating fresh ones"""
        pre_existing = DailyMeal.objects.create(
            meal_plan=self.plan,
            date=datetime.date(2026, 5, 1),
            meal_type=MealType.BREAKFAST,
        )
        pre_pk = pre_existing.pk
        response = self.client.post(self._generate_url(), {'wipe': True}, format='json')
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
        response = self.client.post(self._generate_url(), {'wipe': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(DailyMeal.objects.filter(pk=pre_pk).exists())


class MealSettingsDayToggleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def _create_plan_and_settings(self):
        plan = MealPlan.objects.create(name='Plan', start_date='2026-05-01', user=self.user)
        settings = MealSettings.objects.create(meal_plan=plan)
        return plan, settings

    def test_new_settings_default_all_days_true(self):
        _, settings = self._create_plan_and_settings()
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            self.assertTrue(getattr(settings, f'{day}_enabled'), f'{day}_enabled should default to True')

    def test_day_toggles_in_api_response(self):
        _, settings = self._create_plan_and_settings()
        url = reverse('mealsettings-detail', args=[settings.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ['monday_enabled', 'tuesday_enabled', 'wednesday_enabled',
                      'thursday_enabled', 'friday_enabled', 'saturday_enabled', 'sunday_enabled']:
            self.assertIn(field, response.data)
            self.assertTrue(response.data[field])

    def test_patch_day_toggles(self):
        _, settings = self._create_plan_and_settings()
        url = reverse('mealsettings-detail', args=[settings.pk])
        response = self.client.patch(
            url,
            {'saturday_enabled': False, 'sunday_enabled': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['saturday_enabled'])
        self.assertFalse(response.data['sunday_enabled'])
        self.assertTrue(response.data['monday_enabled'])

    def test_patch_day_toggle_persists(self):
        _, settings = self._create_plan_and_settings()
        url = reverse('mealsettings-detail', args=[settings.pk])
        self.client.patch(url, {'saturday_enabled': False}, format='json')
        settings.refresh_from_db()
        self.assertFalse(settings.saturday_enabled)


class MealPlanStartDateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='startdate@example.com',
            email='startdate@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_without_start_date_returns_400(self):
        url = reverse('mealplan-list')
        response = self.client.post(url, {'name': 'Test Plan'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', response.data)

    def test_create_with_start_date_succeeds(self):
        url = reverse('mealplan-list')
        response = self.client.post(url, {'name': 'Test Plan', 'start_date': '2026-05-01'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['start_date'], '2026-05-01')

    def test_start_date_in_list_response(self):
        MealPlan.objects.create(name='Plan A', start_date='2026-05-01', user=self.user)
        url = reverse('mealplan-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', response.data[0])

    def test_start_date_in_detail_response(self):
        plan = MealPlan.objects.create(name='Plan A', start_date='2026-05-01', user=self.user)
        url = reverse('mealplan-detail', args=[plan.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['start_date'], '2026-05-01')


class DailyMealModelTest(APITestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(name='Test Plan', start_date='2026-05-01')

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
        self.meal_plan = MealPlan.objects.create(name='Serializer Plan', start_date='2026-05-01')
        self.daily_meal = DailyMeal.objects.create(
            meal_plan=self.meal_plan,
            date=datetime.date(2026, 5, 4),
            meal_type=MealType.BREAKFAST,
        )

    def test_serializer_exposes_date(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertIn('date', serializer.data)
        self.assertEqual(serializer.data['date'], '2026-05-04')

    def test_serializer_exposes_day_of_week(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertIn('day_of_week', serializer.data)
        self.assertEqual(serializer.data['day_of_week'], 1)

    def test_serializer_does_not_expose_week(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertNotIn('week', serializer.data)

    def test_serializer_does_not_expose_day(self):
        serializer = DailyMealSerializer(self.daily_meal)
        self.assertNotIn('day', serializer.data)
