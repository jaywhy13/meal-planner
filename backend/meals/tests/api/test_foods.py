from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from meals.factories import FoodFactory, UserFactory
from meals.models import Food


class FoodSearchTests(APITestCase):
    def test_search_matches_are_capped_at_ten(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        for index in range(15):
            FoodFactory(name=f"Apple Variety {index}")
        url = reverse("food-search")

        response = self.client.get(url, {"q": "apple"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

    def test_blank_query_returns_first_ten_foods(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        for index in range(15):
            FoodFactory(name=f"Food {index}")
        url = reverse("food-search")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)


class FoodListTests(APITestCase):
    def test_list_returns_all_foods_uncapped(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        for index in range(15):
            FoodFactory(name=f"Food {index}")
        url = reverse("food-list")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 15)


class FoodRetrieveTests(APITestCase):
    def test_retrieve_returns_food(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        food = FoodFactory(name="Banana", category="Fruit")
        url = reverse("food-detail", args=[food.id])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], food.id)
        self.assertEqual(response.data["name"], "Banana")
        self.assertEqual(response.data["category"], "Fruit")

    def test_retrieve_missing_food_returns_not_found(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("food-detail", args=[999999])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FoodCreateTests(APITestCase):
    def test_create_persists_food(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("food-list")

        response = self.client.post(url, {"name": "Carrot", "category": "Vegetable"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Food.objects.filter(name="Carrot", category="Vegetable").exists())


class FoodUpdateTests(APITestCase):
    def test_update_replaces_food_fields(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        food = FoodFactory(name="Old Name", category="Old Category")
        url = reverse("food-detail", args=[food.id])

        response = self.client.put(url, {"name": "New Name", "category": "New Category"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        food.refresh_from_db()
        self.assertEqual(food.name, "New Name")
        self.assertEqual(food.category, "New Category")

    def test_update_missing_food_returns_not_found(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("food-detail", args=[999999])

        response = self.client.put(url, {"name": "New Name", "category": "New Category"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_changes_only_provided_fields(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        food = FoodFactory(name="Old Name", category="Old Category")
        url = reverse("food-detail", args=[food.id])

        response = self.client.patch(url, {"category": "New Category"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        food.refresh_from_db()
        self.assertEqual(food.name, "Old Name")
        self.assertEqual(food.category, "New Category")


class FoodDeleteTests(APITestCase):
    def test_delete_removes_food(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        food = FoodFactory(name="Doomed Food")
        url = reverse("food-detail", args=[food.id])

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Food.objects.filter(id=food.id).exists())

    def test_delete_missing_food_returns_not_found(self):
        user = UserFactory()
        self.client.force_authenticate(user=user)
        url = reverse("food-detail", args=[999999])

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
