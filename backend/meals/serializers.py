from rest_framework import serializers
from .models import MealPlan, Food, DailyMeal, Meal, MealSettings


class FoodSerializer(serializers.Serializer):
    """Serializes `FoodData` value objects. Also used nested (read-only) under
    `MealSerializer`/`MealSuggestionSerializer`, where attribute access works
    just as well against ORM `Food` instances."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    created_at = serializers.DateTimeField(read_only=True)


class MealSuggestionSerializer(serializers.Serializer):
    """Serializes `MealSuggestionData` value objects, never ORM `MealSuggestion` rows."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(allow_blank=True, required=False, default="")
    foods = FoodSerializer(many=True, read_only=True)
    meal_type = serializers.CharField()
    is_healthy = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)


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
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if foods is not None:
            instance.foods.set(foods)
        return instance


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
