from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from meals.factories import FoodFactory, MealFactory, UserFactory
from meals.models import Meal


class MealCrudTests(APITestCase):
    def test_create_meal_with_foods(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        eggs = FoodFactory(name="Eggs")
        meal_list_creation_url = reverse("meal-list")

        response = self.client.post(
            meal_list_creation_url,
            {"name": "Scramble", "food_ids": [eggs.id], "notes": "Quick"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_meal = Meal.objects.get(name="Scramble")
        self.assertEqual(created_meal.user, user)
        self.assertIn(eggs, created_meal.foods.all())

    def test_create_meal_requires_name(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal_list_creation_url = reverse("meal-list")

        response = self.client.post(meal_list_creation_url, {"notes": "No name"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_list_returns_only_own_meals(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        own_meal = MealFactory(user=user, name="Mine")
        other_user = UserFactory()
        their_meal = MealFactory(user=other_user, name="Theirs")
        meal_list_url = reverse("meal-list")

        response = self.client.get(meal_list_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [meal["id"] for meal in response.data]
        self.assertIn(own_meal.id, returned_ids)
        self.assertTrue(their_meal.id not in returned_ids)

    def test_name_search_filters_results(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        chicken_meal = MealFactory(user=user, name="Chicken Bowl")
        MealFactory(user=user, name="Veggie Wrap")
        meal_list_url = reverse("meal-list")

        response = self.client.get(meal_list_url, {"q": "chicken"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [meal["id"] for meal in response.data]
        self.assertEqual(returned_ids, [chicken_meal.id])

    def test_update_own_meal(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal = MealFactory(user=user, name="Old Name")
        meal_detail_url = reverse("meal-detail", args=[meal.pk])

        response = self.client.patch(meal_detail_url, {"name": "New Name"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        meal.refresh_from_db()
        self.assertEqual(meal.name, "New Name")

    def test_delete_own_meal(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        meal = MealFactory(user=user, name="To Delete")
        meal_detail_url = reverse("meal-detail", args=[meal.pk])

        response = self.client.delete(meal_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Meal.objects.filter(pk=meal.pk).exists())

    def test_cannot_retrieve_another_users_meal(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        other_user = UserFactory()
        foreign_meal = MealFactory(user=other_user, name="Theirs")
        meal_detail_url = reverse("meal-detail", args=[foreign_meal.pk])

        response = self.client.get(meal_detail_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
