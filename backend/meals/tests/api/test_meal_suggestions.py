from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from meals.factories import FoodFactory, MealSuggestionFactory
from meals.models import MealType


class MealSuggestionListTests(APITestCase):
    def test_list_returns_all_healthy_suggestions(self):
        healthy_suggestion = MealSuggestionFactory(name="Oatmeal", is_healthy=True)
        MealSuggestionFactory(name="Fries", is_healthy=False)
        url = reverse("mealsuggestion-list")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {suggestion["id"] for suggestion in response.data}
        self.assertEqual(returned_ids, {healthy_suggestion.id})

    def test_list_includes_nested_foods(self):
        apple = FoodFactory(name="Apple")
        suggestion = MealSuggestionFactory(name="Fruit Bowl", is_healthy=True, foods=[apple])
        url = reverse("mealsuggestion-list")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_suggestion = next(item for item in response.data if item["id"] == suggestion.id)
        self.assertEqual([food["id"] for food in returned_suggestion["foods"]], [apple.id])


class MealSuggestionRetrieveTests(APITestCase):
    def test_retrieve_returns_suggestion(self):
        suggestion = MealSuggestionFactory(name="Oatmeal", is_healthy=True)
        url = reverse("mealsuggestion-detail", args=[suggestion.id])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], suggestion.id)
        self.assertEqual(response.data["name"], "Oatmeal")

    def test_retrieve_missing_suggestion_returns_not_found(self):
        url = reverse("mealsuggestion-detail", args=[999999])

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MealSuggestionByMealTypeTests(APITestCase):
    def test_by_meal_type_filters_to_requested_type(self):
        breakfast_suggestion = MealSuggestionFactory(name="Oatmeal", meal_type=MealType.BREAKFAST, is_healthy=True)
        MealSuggestionFactory(name="Salad", meal_type=MealType.LUNCH, is_healthy=True)
        url = reverse("mealsuggestion-by-meal-type")

        response = self.client.get(url, {"meal_type": MealType.BREAKFAST}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [suggestion["id"] for suggestion in response.data]
        self.assertEqual(returned_ids, [breakfast_suggestion.id])

    def test_by_meal_type_without_type_returns_all_healthy_suggestions(self):
        breakfast_suggestion = MealSuggestionFactory(name="Oatmeal", meal_type=MealType.BREAKFAST, is_healthy=True)
        lunch_suggestion = MealSuggestionFactory(name="Salad", meal_type=MealType.LUNCH, is_healthy=True)
        MealSuggestionFactory(name="Fries", meal_type=MealType.LUNCH, is_healthy=False)
        url = reverse("mealsuggestion-by-meal-type")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {suggestion["id"] for suggestion in response.data}
        self.assertEqual(returned_ids, {breakfast_suggestion.id, lunch_suggestion.id})
