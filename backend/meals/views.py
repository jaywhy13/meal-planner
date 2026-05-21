from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import DailyMeal, Food, MealPlan, MealSettings, MealSuggestion
from .serializers import (
    DailyMealSerializer,
    FoodSerializer,
    MealPlanListSerializer,
    MealPlanSerializer,
    MealSettingsSerializer,
    MealSuggestionSerializer,
)


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return MealPlanListSerializer
        return MealPlanSerializer

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def generate_meal_plan(self, request, pk=None):
        meal_plan = self.get_object()

        meal_settings, _ = MealSettings.objects.get_or_create(meal_plan=meal_plan)
        suggestions = MealSuggestion.objects.filter(is_healthy=True)

        for week in range(1, 5):
            for day in range(1, 6):
                enabled_meal_types = []
                if meal_settings.breakfast_enabled:
                    enabled_meal_types.append("breakfast")
                if meal_settings.lunch_enabled:
                    enabled_meal_types.append("lunch")
                if meal_settings.dinner_enabled:
                    enabled_meal_types.append("dinner")
                if meal_settings.snack_enabled:
                    enabled_meal_types.append("snack")

                for meal_type in enabled_meal_types:
                    existing_meal, created = DailyMeal.objects.get_or_create(
                        meal_plan=meal_plan, week=week, day=day, meal_type=meal_type
                    )
                    if created and suggestions.exists():
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Food.objects.filter(
            Q(user=self.request.user) | Q(user=None)
        ).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        base_qs = Food.objects.filter(Q(user=request.user) | Q(user=None))
        if query:
            foods = base_qs.filter(name__icontains=query)[:10]
        else:
            foods = base_qs[:10]
        serializer = self.get_serializer(foods, many=True)
        return Response(serializer.data)


class DailyMealViewSet(viewsets.ModelViewSet):
    queryset = DailyMeal.objects.all()
    serializer_class = DailyMealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DailyMeal.objects.filter(meal_plan__user=self.request.user)
        meal_plan_id = self.request.query_params.get("meal_plan")
        if meal_plan_id:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset

    def perform_create(self, serializer):
        meal_plan = serializer.validated_data.get("meal_plan")
        if meal_plan and meal_plan.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this meal plan.")
        serializer.save()


class MealSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MealSuggestion.objects.all()
    serializer_class = MealSuggestionSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def by_meal_type(self, request):
        meal_type = request.query_params.get("meal_type")
        if meal_type:
            suggestions = MealSuggestion.objects.filter(meal_type=meal_type, is_healthy=True)
        else:
            suggestions = MealSuggestion.objects.filter(is_healthy=True)
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)


class MealSettingsViewSet(viewsets.ModelViewSet):
    queryset = MealSettings.objects.all()
    serializer_class = MealSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = MealSettings.objects.filter(meal_plan__user=self.request.user)
        meal_plan_id = self.request.query_params.get("meal_plan")
        if meal_plan_id:
            queryset = queryset.filter(meal_plan_id=meal_plan_id)
        return queryset
