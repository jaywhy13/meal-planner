from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from .models import MealPlan, Food, DailyMeal, MealSuggestion, MealSettings
from .serializers import (
    MealPlanSerializer, MealPlanListSerializer, FoodSerializer,
    DailyMealSerializer, MealSuggestionSerializer, MealSettingsSerializer
)


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MealPlanListSerializer
        return MealPlanSerializer
    
    @action(detail=True, methods=['post'])
    def generate_meal_plan(self, request, pk=None):
        """Generate a meal plan with suggestions for 4 weeks"""
        meal_plan = self.get_object()
        
        # Get or create meal settings
        meal_settings, created = MealSettings.objects.get_or_create(meal_plan=meal_plan)
        
        # Get healthy meal suggestions
        suggestions = MealSuggestion.objects.filter(is_healthy=True)
        
        # Generate meals for 4 weeks, 5 days each
        for week in range(1, 5):  # Weeks 1-4
            for day in range(1, 6):  # Days 1-5 (Monday-Friday)
                # Get enabled meal types from settings
                enabled_meal_types = []
                if meal_settings.breakfast_enabled:
                    enabled_meal_types.append('breakfast')
                if meal_settings.lunch_enabled:
                    enabled_meal_types.append('lunch')
                if meal_settings.dinner_enabled:
                    enabled_meal_types.append('dinner')
                if meal_settings.snack_enabled:
                    enabled_meal_types.append('snack')
                
                for meal_type in enabled_meal_types:
                    # Check if meal already exists
                    existing_meal, created = DailyMeal.objects.get_or_create(
                        meal_plan=meal_plan,
                        week=week,
                        day=day,
                        meal_type=meal_type
                    )
                    
                    if created and suggestions.exists():
                        # Assign a random suggestion for this meal type
                        meal_suggestion = suggestions.filter(meal_type=meal_type).first()
                        if meal_suggestion:
                            existing_meal.foods.set(meal_suggestion.foods.all())
                            existing_meal.notes = meal_suggestion.description
                            existing_meal.save()
        
        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search foods by name"""
        query = request.query_params.get('q', '')
        if query:
            foods = Food.objects.filter(name__icontains=query)[:10]
        else:
            foods = Food.objects.all()[:10]
        
        serializer = self.get_serializer(foods, many=True)
        return Response(serializer.data)


class DailyMealViewSet(viewsets.ModelViewSet):
    queryset = DailyMeal.objects.all()
    serializer_class = DailyMealSerializer
    
    def get_queryset(self):
        queryset = DailyMeal.objects.all()
        meal_plan_id = self.request.query_params.get('meal_plan')
        if meal_plan_id:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset


class MealSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MealSuggestion.objects.all()
    serializer_class = MealSuggestionSerializer
    
    @action(detail=False, methods=['get'])
    def by_meal_type(self, request):
        """Get suggestions filtered by meal type"""
        meal_type = request.query_params.get('meal_type')
        if meal_type:
            suggestions = MealSuggestion.objects.filter(
                meal_type=meal_type, 
                is_healthy=True
            )
        else:
            suggestions = MealSuggestion.objects.filter(is_healthy=True)
        
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)


class MealSettingsViewSet(viewsets.ModelViewSet):
    queryset = MealSettings.objects.all()
    serializer_class = MealSettingsSerializer
    
    def get_queryset(self):
        queryset = MealSettings.objects.all()
        meal_plan_id = self.request.query_params.get('meal_plan')
        if meal_plan_id:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset