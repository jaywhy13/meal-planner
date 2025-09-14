from rest_framework import serializers
from .models import MealPlan, Food, DailyMeal, MealSuggestion, MealSettings


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name', 'category', 'created_at']


class MealSuggestionSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)
    
    class Meta:
        model = MealSuggestion
        fields = ['id', 'name', 'description', 'foods', 'meal_type', 'is_healthy', 'created_at']


class DailyMealSerializer(serializers.ModelSerializer):
    foods = FoodSerializer(many=True, read_only=True)
    food_ids = serializers.PrimaryKeyRelatedField(
        queryset=Food.objects.all(),
        source='foods',
        many=True,
        write_only=True
    )
    
    class Meta:
        model = DailyMeal
        fields = ['id', 'meal_plan', 'week', 'day', 'meal_type', 'foods', 'food_ids', 'notes']
    
    def create(self, validated_data):
        print("Received data:", validated_data)
        foods = validated_data.pop('foods', [])
        print("After popping foods:", validated_data)
        daily_meal = DailyMeal.objects.create(**validated_data)
        daily_meal.foods.set(foods)
        return daily_meal
    
    def update(self, instance, validated_data):
        foods = validated_data.pop('foods', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.foods.set(foods)
        return instance


class MealSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSettings
        fields = ['id', 'breakfast_enabled', 'lunch_enabled', 'dinner_enabled', 'snack_enabled', 'created_at', 'updated_at']


class MealPlanSerializer(serializers.ModelSerializer):
    daily_meals = DailyMealSerializer(many=True, read_only=True)
    meal_settings = MealSettingsSerializer(read_only=True)
    
    class Meta:
        model = MealPlan
        fields = ['id', 'name', 'created_at', 'updated_at', 'daily_meals', 'meal_settings']


class MealPlanListSerializer(serializers.ModelSerializer):
    """Simplified serializer for meal plan lists"""
    class Meta:
        model = MealPlan
        fields = ['id', 'name', 'created_at', 'updated_at']
