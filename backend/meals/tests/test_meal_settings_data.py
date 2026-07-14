import datetime

from django.test import SimpleTestCase

from meals.models import MealType
from meals.repositories import MealSettingsData


def build_meal_settings_data(**overrides) -> MealSettingsData:
    defaults = dict(
        breakfast_enabled=True,
        lunch_enabled=True,
        dinner_enabled=True,
        snack_enabled=True,
        monday_enabled=True,
        tuesday_enabled=True,
        wednesday_enabled=True,
        thursday_enabled=True,
        friday_enabled=True,
        saturday_enabled=True,
        sunday_enabled=True,
    )
    defaults.update(overrides)
    return MealSettingsData(**defaults)


class MealSettingsDataTests(SimpleTestCase):
    def test_enabled_meal_types_excludes_disabled(self):
        settings = build_meal_settings_data(breakfast_enabled=False, snack_enabled=False)
        self.assertEqual(settings.enabled_meal_types(), [MealType.LUNCH, MealType.DINNER])

    def test_is_week_day_enabled_reflects_flags(self):
        settings = build_meal_settings_data(saturday_enabled=False)
        self.assertFalse(settings.is_week_day_enabled(6))
        self.assertTrue(settings.is_week_day_enabled(1))

    def test_is_week_day_enabled_rejects_invalid_weekday(self):
        settings = build_meal_settings_data()
        with self.assertRaises(ValueError):
            settings.is_week_day_enabled(8)

    def test_get_enabled_days_skips_disabled_weekdays(self):
        settings = build_meal_settings_data(saturday_enabled=False, sunday_enabled=False)
        enabled_days = settings.get_enabled_days(datetime.date(2026, 5, 1), datetime.date(2026, 5, 7))
        weekdays = {day.isoweekday() for day in enabled_days}
        self.assertNotIn(6, weekdays)
        self.assertNotIn(7, weekdays)

    def test_get_enabled_days_inclusive_of_bounds(self):
        settings = build_meal_settings_data()
        enabled_days = settings.get_enabled_days(datetime.date(2026, 5, 1), datetime.date(2026, 5, 3))
        self.assertEqual(
            enabled_days,
            [datetime.date(2026, 5, 1), datetime.date(2026, 5, 2), datetime.date(2026, 5, 3)],
        )
