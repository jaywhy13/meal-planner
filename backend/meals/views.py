import calendar
from datetime import date, timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import MealPlan, Food, DailyMeal, MealSuggestion, MealSettings
from .serializers import (
    MealPlanSerializer, MealPlanListSerializer, FoodSerializer,
    DailyMealSerializer, MealSuggestionSerializer, MealSettingsSerializer
)
from .services import DailyMealService, MealPlanService, MealSettingsService

meal_plan_service = MealPlanService()
daily_meal_service = DailyMealService()
meal_settings_service = MealSettingsService()


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MealPlanListSerializer
        return MealPlanSerializer

    def get_queryset(self):
        return meal_plan_service.list_for_user(self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_meal_plan(self, request, pk=None):
        """Generate meals for the full calendar month of the plan's start_date"""
        meal_plan = self.get_object()
        wipe = request.data.get('wipe', False)

        meal_settings, _ = MealSettings.objects.get_or_create(meal_plan=meal_plan)
        suggestions = MealSuggestion.objects.filter(is_healthy=True)

        if wipe:
            meal_plan.daily_meals.all().delete()

        # Map ISO weekday (1-7) to MealSettings field name
        day_field_map = {
            1: 'monday_enabled', 2: 'tuesday_enabled', 3: 'wednesday_enabled',
            4: 'thursday_enabled', 5: 'friday_enabled', 6: 'saturday_enabled',
            7: 'sunday_enabled',
        }

        enabled_meal_types = [
            mt for mt, field in [
                ('breakfast', 'breakfast_enabled'), ('lunch', 'lunch_enabled'),
                ('dinner', 'dinner_enabled'), ('snack', 'snack_enabled'),
            ] if getattr(meal_settings, field)
        ]

        start = meal_plan.start_date.replace(day=1)
        _, days_in_month = calendar.monthrange(start.year, start.month)

        for offset in range(days_in_month):
            current_date = start + timedelta(days=offset)
            day_field = day_field_map[current_date.isoweekday()]
            if not getattr(meal_settings, day_field):
                continue

            for meal_type in enabled_meal_types:
                meal, created = DailyMeal.objects.get_or_create(
                    meal_plan=meal_plan,
                    date=current_date,
                    meal_type=meal_type,
                )
                if created and suggestions.exists():
                    suggestion = suggestions.filter(meal_type=meal_type).first()
                    if suggestion:
                        meal.foods.set(suggestion.foods.all())
                        meal.notes = suggestion.description
                        meal.save()

        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meal_plan_id = self.request.query_params.get('meal_plan')
        return daily_meal_service.list_for_user(
            self.request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )

    def perform_create(self, serializer):
        meal_plan = serializer.validated_data.get("meal_plan")
        if meal_plan and meal_plan.user != self.request.user:
            raise PermissionDenied("You do not own this meal plan.")
        serializer.save()


class MealSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MealSuggestion.objects.all()
    serializer_class = MealSuggestionSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meal_plan_id = self.request.query_params.get('meal_plan')
        return meal_settings_service.list_for_user(
            self.request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )