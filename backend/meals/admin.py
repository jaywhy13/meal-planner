from django.contrib import admin
from .models import MealPlan, Food, DailyMeal, Meal, MealSuggestion, MealSettings


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "created_at"]
    search_fields = ["name", "category"]
    list_filter = ["category"]
    readonly_fields = ["created_at"]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created_at", "updated_at"]
    list_filter = ["user"]
    search_fields = ["name", "notes"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["foods"]


@admin.register(DailyMeal)
class DailyMealAdmin(admin.ModelAdmin):
    list_display = ["meal_plan", "date", "day_of_week", "meal_type", "meal"]
    list_filter = ["meal_type", "day_of_week", "meal_plan"]
    search_fields = ["meal_plan__name", "meal__name"]


@admin.register(MealSettings)
class MealSettingsAdmin(admin.ModelAdmin):
    list_display = ["meal_plan", "breakfast_enabled", "lunch_enabled", "dinner_enabled", "snack_enabled"]
    list_filter = ["breakfast_enabled", "lunch_enabled", "dinner_enabled", "snack_enabled"]
    search_fields = ["meal_plan__name"]


@admin.register(MealSuggestion)
class MealSuggestionAdmin(admin.ModelAdmin):
    list_display = ["name", "meal_type", "is_healthy", "created_at"]
    list_filter = ["meal_type", "is_healthy"]
    search_fields = ["name", "description"]
    filter_horizontal = ["foods"]
