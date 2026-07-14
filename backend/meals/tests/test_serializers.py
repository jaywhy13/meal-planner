import datetime

from django.test import TestCase

from meals.factories import DailyMealFactory
from meals.models import MealType
from meals.serializers import DailyMealSerializer


class DailyMealSerializerTests(TestCase):
    def test_serializer_exposes_date(self):
        daily_meal = DailyMealFactory(date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST)
        serializer = DailyMealSerializer(daily_meal)
        self.assertEqual(serializer.data["date"], "2026-05-04")

    def test_serializer_exposes_day_of_week(self):
        daily_meal = DailyMealFactory(date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST)
        serializer = DailyMealSerializer(daily_meal)
        self.assertEqual(serializer.data["day_of_week"], 1)

    def test_serializer_does_not_expose_week(self):
        daily_meal = DailyMealFactory()
        serializer = DailyMealSerializer(daily_meal)
        self.assertNotIn("week", serializer.data)

    def test_serializer_does_not_expose_day(self):
        daily_meal = DailyMealFactory()
        serializer = DailyMealSerializer(daily_meal)
        self.assertNotIn("day", serializer.data)
