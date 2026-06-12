import datetime

from django.db import IntegrityError
from django.test import TestCase

from meals.factories import DailyMealFactory, MealPlanFactory
from meals.models import MealType


class DailyMealModelTests(TestCase):
    def test_monday_sets_day_of_week_1(self):
        daily_meal = DailyMealFactory(
            date=datetime.date(2026, 5, 4), meal_type=MealType.BREAKFAST
        )
        self.assertEqual(daily_meal.day_of_week, 1)

    def test_sunday_sets_day_of_week_7(self):
        daily_meal = DailyMealFactory(date=datetime.date(2026, 5, 10), meal_type=MealType.LUNCH)
        self.assertEqual(daily_meal.day_of_week, 7)

    def test_duplicate_meal_plan_date_meal_type_raises_integrity_error(self):
        plan = MealPlanFactory()
        DailyMealFactory(meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.DINNER)
        with self.assertRaises(IntegrityError):
            DailyMealFactory(
                meal_plan=plan, date=datetime.date(2026, 5, 4), meal_type=MealType.DINNER
            )
