from django.db import models
from django.contrib.auth.models import User


class MealPlan(models.Model):
    """Represents a meal plan anchored to a calendar month"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="meal_plans")
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Food(models.Model):
    """Represents a food item that can be used in meal plans."""

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MealType(models.TextChoices):
    BREAKFAST = "breakfast", "Breakfast"
    LUNCH = "lunch", "Lunch"
    DINNER = "dinner", "Dinner"
    SNACK = "snack", "Snack"


class Meal(models.Model):
    """A reusable meal — a set of foods with notes — that can be assigned to many daily slots"""

    foods = models.ManyToManyField(Food, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.notes[:50] if self.notes else f"Meal #{self.pk}"


class DailyMeal(models.Model):
    """A meal of a given type on a specific date within a meal plan"""

    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="daily_meals")
    date = models.DateField()
    day_of_week = models.PositiveSmallIntegerField(db_index=True)  # ISO weekday: 1=Mon, 7=Sun
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    meal = models.ForeignKey(
        Meal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="daily_meals",
    )

    class Meta:
        unique_together = ["meal_plan", "date", "meal_type"]
        ordering = ["date", "meal_type"]

    def save(self, *args, **kwargs):
        self.day_of_week = self.date.isoweekday()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.meal_plan.name} - {self.date} - {self.get_meal_type_display()}"


class MealSettings(models.Model):
    """Settings for which meal types and days of the week are enabled in a meal plan"""

    meal_plan = models.OneToOneField(MealPlan, on_delete=models.CASCADE, related_name="meal_settings")
    breakfast_enabled = models.BooleanField(default=True)
    lunch_enabled = models.BooleanField(default=True)
    dinner_enabled = models.BooleanField(default=True)
    snack_enabled = models.BooleanField(default=True)
    monday_enabled = models.BooleanField(default=True)
    tuesday_enabled = models.BooleanField(default=True)
    wednesday_enabled = models.BooleanField(default=True)
    thursday_enabled = models.BooleanField(default=True)
    friday_enabled = models.BooleanField(default=True)
    saturday_enabled = models.BooleanField(default=True)
    sunday_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.meal_plan.name}"


class MealSuggestion(models.Model):
    """Pre-defined meal suggestions for healthy meal planning"""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    foods = models.ManyToManyField(Food)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    is_healthy = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_meal_type_display()})"
