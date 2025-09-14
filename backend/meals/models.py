from django.db import models
from django.contrib.auth.models import User


class MealPlan(models.Model):
    """Represents a meal plan with a name and date range"""
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Food(models.Model):
    """Represents a food item that can be used in meal plans"""
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MealType(models.TextChoices):
    BREAKFAST = 'breakfast', 'Breakfast'
    LUNCH = 'lunch', 'Lunch'
    DINNER = 'dinner', 'Dinner'
    SNACK = 'snack', 'Snack'


class DailyMeal(models.Model):
    """Represents meals for a specific day in a meal plan"""
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='daily_meals')
    week = models.PositiveIntegerField()  # Week 1-4
    day = models.PositiveIntegerField()   # Day 1-5 (Monday-Friday)
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    foods = models.ManyToManyField(Food, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['meal_plan', 'week', 'day', 'meal_type']
        ordering = ['week', 'day', 'meal_type']
    
    def __str__(self):
        return f"{self.meal_plan.name} - Week {self.week}, Day {self.day} - {self.get_meal_type_display()}"


class MealSettings(models.Model):
    """Settings for which meal types are enabled in a meal plan"""
    meal_plan = models.OneToOneField(MealPlan, on_delete=models.CASCADE, related_name='meal_settings')
    breakfast_enabled = models.BooleanField(default=True)
    lunch_enabled = models.BooleanField(default=True)
    dinner_enabled = models.BooleanField(default=True)
    snack_enabled = models.BooleanField(default=True)
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