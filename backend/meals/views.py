from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import MealPlan, Food, DailyMeal, MealSettings
from .serializers import (
    MealPlanSerializer,
    MealPlanListSerializer,
    FoodSerializer,
    DailyMealSerializer,
    MealSerializer,
    MealSuggestionSerializer,
    MealSettingsSerializer,
)
from .services import (
    DailyMealService,
    MealPlanGenerationService,
    MealPlanService,
    MealService,
    MealSettingsService,
    MealSuggestionService,
)

meal_plan_service = MealPlanService()
meal_plan_generation_service = MealPlanGenerationService()
meal_service = MealService()
daily_meal_service = DailyMealService()
meal_settings_service = MealSettingsService()
meal_suggestion_service = MealSuggestionService()


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return MealPlanListSerializer
        return MealPlanSerializer

    def get_queryset(self):
        return meal_plan_service.list_for_user(self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def generate_meal_plan(self, request, pk=None):
        """Generate meals for the full calendar month of the plan's start_date"""
        meal_plan = self.get_object()
        wipe = request.data.get("wipe", False)
        meal_plan_generation_service.generate(meal_plan, wipe=wipe)
        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)


class MealViewSet(viewsets.ModelViewSet):
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        name = self.request.query_params.get("q")
        return meal_service.list_for_user(self.request.user.id, name=name)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not own this meal.")
        serializer.save()


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search foods by name"""
        query = request.query_params.get("q", "")
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
        meal_plan_id = self.request.query_params.get("meal_plan")
        return daily_meal_service.list_for_user(
            self.request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )

    def perform_create(self, serializer):
        meal_plan = serializer.validated_data.get("meal_plan")
        if meal_plan and meal_plan.user != self.request.user:
            raise PermissionDenied("You do not own this meal plan.")
        serializer.save()


class MealSuggestionViewSet(viewsets.ViewSet):
    """Plain ViewSet: `meal_suggestion_service` returns `MealSuggestionData` value
    objects only, never ORM `MealSuggestion` instances or querysets."""

    permission_classes = [AllowAny]

    def list(self, request):
        suggestions = meal_suggestion_service.list_healthy()
        serializer = MealSuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        suggestion = meal_suggestion_service.get(int(pk))
        if suggestion is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MealSuggestionSerializer(suggestion)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_meal_type(self, request):
        """Get suggestions filtered by meal type"""
        meal_type = request.query_params.get("meal_type")
        suggestions = meal_suggestion_service.list_healthy(meal_type=meal_type)
        serializer = MealSuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)


class MealSettingsViewSet(viewsets.ModelViewSet):
    queryset = MealSettings.objects.all()
    serializer_class = MealSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        meal_plan_id = self.request.query_params.get("meal_plan")
        return meal_settings_service.list_for_user(
            self.request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )
