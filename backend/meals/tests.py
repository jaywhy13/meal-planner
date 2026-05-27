from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import MealPlan, MealSettings


class MealSettingsDayToggleTests(APITestCase):
    def _create_plan_and_settings(self):
        plan = MealPlan.objects.create(name='Plan', start_date='2026-05-01')
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
        MealPlan.objects.create(name='Plan A', start_date='2026-05-01')
        url = reverse('mealplan-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', response.data[0])

    def test_start_date_in_detail_response(self):
        plan = MealPlan.objects.create(name='Plan A', start_date='2026-05-01')
        url = reverse('mealplan-detail', args=[plan.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['start_date'], '2026-05-01')
