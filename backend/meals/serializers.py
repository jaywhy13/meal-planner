from rest_framework import serializers
from .models import MealPlan, Food, DailyMeal, MealSuggestion, MealSettings, MealType


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ["id", "name", "category", "created_at"]


class MealSuggestionSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)

    class Meta:
        model = MealSuggestion
        fields = ["id", "name", "description", "foods", "meal_type", "is_healthy", "created_at"]


class FoodDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()


class DailyMealSerializer(serializers.Serializer):
    """Serializes a DailyMealData value object for the daily-meals endpoint."""

    id = serializers.IntegerField(read_only=True)
    meal_plan = serializers.IntegerField(source="meal_plan_id")
    date = serializers.DateField()
    day_of_week = serializers.IntegerField(read_only=True)
    meal_type = serializers.CharField()
    foods = FoodDataSerializer(many=True, read_only=True)
    notes = serializers.CharField()


class DailyMealWriteSerializer(serializers.Serializer):
    """Validates incoming payloads for creating/updating a daily meal slot."""

    meal_plan = serializers.PrimaryKeyRelatedField(queryset=MealPlan.objects.all())
    date = serializers.DateField()
    meal_type = serializers.ChoiceField(choices=MealType.choices)
    food_ids = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(), many=True, required=False, default=list
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class NestedDailyMealSerializer(serializers.ModelSerializer):
    foods = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = DailyMeal
        fields = ["id", "meal_plan", "date", "day_of_week", "meal_type", "foods", "notes"]

    def get_foods(self, daily_meal):
        if daily_meal.meal is None:
            return []
        return FoodSerializer(daily_meal.meal.foods.all(), many=True).data

    def get_notes(self, daily_meal):
        return daily_meal.meal.notes if daily_meal.meal else ""


class MealSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSettings
        fields = [
            "id",
            "breakfast_enabled",
            "lunch_enabled",
            "dinner_enabled",
            "snack_enabled",
            "monday_enabled",
            "tuesday_enabled",
            "wednesday_enabled",
            "thursday_enabled",
            "friday_enabled",
            "saturday_enabled",
            "sunday_enabled",
            "created_at",
            "updated_at",
        ]


class MealPlanSerializer(serializers.ModelSerializer):
    daily_meals = NestedDailyMealSerializer(many=True, read_only=True)
    meal_settings = MealSettingsSerializer(read_only=True)

    class Meta:
        model = MealPlan
        fields = ["id", "name", "start_date", "created_at", "updated_at", "daily_meals", "meal_settings"]


class MealPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = ["id", "name", "start_date", "created_at", "updated_at"]
