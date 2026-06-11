from rest_framework import serializers
from .models import MealPlan, Food, DailyMeal, Meal, MealSuggestion, MealSettings


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ["id", "name", "category", "created_at"]


class MealSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)
    food_ids = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(), source="foods", many=True, write_only=True, required=False
    )

    class Meta:
        model = Meal
        fields = ["id", "name", "foods", "food_ids", "notes", "created_at", "updated_at"]

    def create(self, validated_data):
        foods = validated_data.pop("foods", [])
        meal = Meal.objects.create(**validated_data)
        meal.foods.set(foods)
        return meal

    def update(self, instance, validated_data):
        foods = validated_data.pop("foods", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()
        if foods is not None:
            instance.foods.set(foods)
        return instance


class MealSuggestionSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)

    class Meta:
        model = MealSuggestion
        fields = ["id", "name", "description", "foods", "meal_type", "is_healthy", "created_at"]


class DailyMealSerializer(serializers.ModelSerializer):
    meal = MealSerializer(read_only=True)
    meal_id = serializers.PrimaryKeyRelatedField(
        queryset=Meal.objects.all(), source="meal", write_only=True, required=False, allow_null=True
    )
    day_of_week = serializers.ReadOnlyField()

    class Meta:
        model = DailyMeal
        fields = ["id", "meal_plan", "date", "day_of_week", "meal_type", "meal", "meal_id"]


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
    daily_meals = DailyMealSerializer(many=True, read_only=True)
    meal_settings = MealSettingsSerializer(read_only=True)

    class Meta:
        model = MealPlan
        fields = ["id", "name", "start_date", "created_at", "updated_at", "daily_meals", "meal_settings"]


class MealPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = ["id", "name", "start_date", "created_at", "updated_at"]
