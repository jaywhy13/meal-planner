from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import MealPlan, Food, MealSuggestion, MealSettings
from .serializers import (
    MealPlanSerializer,
    MealPlanListSerializer,
    FoodSerializer,
    DailyMealSerializer,
    DailyMealWriteSerializer,
    MealSuggestionSerializer,
    MealSettingsSerializer,
)
from .services import (
    DailyMealService,
    MealPlanNotOwnedError,
    MealPlanService,
    MealSettingsService,
)

meal_plan_service = MealPlanService()
daily_meal_service = DailyMealService()
meal_settings_service = MealSettingsService()


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return MealPlanListSerializer
        return MealPlanSerializer

    def get_queryset(self):
        if self.action == "list":
            return meal_plan_service.list_for_user(self.request.user.id)
        return meal_plan_service.detail_for_user(self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def generate_meal_plan(self, request, pk=None):
        """Generate meals for the full calendar month of the plan's start_date"""
        meal_plan = self.get_object()
        wipe = request.data.get("wipe", False)
        meal_plan_service.generate_meals(meal_plan.id, wipe)
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


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


class DailyMealViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        meal_plan_id = request.query_params.get("meal_plan")
        daily_meals = daily_meal_service.list_for_user(
            request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )
        return Response(DailyMealSerializer(daily_meals, many=True).data)

    def retrieve(self, request, pk=None):
        daily_meal_id = self._parse_daily_meal_id(pk)
        if daily_meal_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        daily_meal = daily_meal_service.get_for_user(request.user.id, daily_meal_id)
        if daily_meal is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(DailyMealSerializer(daily_meal).data)

    def create(self, request):
        payload = DailyMealWriteSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        fields = self._fields_from(payload.validated_data)
        try:
            daily_meal = daily_meal_service.create(user_id=request.user.id, **fields)
        except MealPlanNotOwnedError:
            raise PermissionDenied("You do not own this meal plan.")
        return Response(DailyMealSerializer(daily_meal).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._write(request, pk, partial=False)

    def partial_update(self, request, pk=None):
        return self._write(request, pk, partial=True)

    def destroy(self, request, pk=None):
        daily_meal_id = self._parse_daily_meal_id(pk)
        if daily_meal_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        existing = daily_meal_service.get_for_user(request.user.id, daily_meal_id)
        if existing is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        daily_meal_service.delete(request.user.id, daily_meal_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _write(self, request, pk, partial):
        daily_meal_id = self._parse_daily_meal_id(pk)
        if daily_meal_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        existing = daily_meal_service.get_for_user(request.user.id, daily_meal_id)
        if existing is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        payload = DailyMealWriteSerializer(data=request.data, partial=partial)
        payload.is_valid(raise_exception=True)
        fields = self._fields_from(payload.validated_data, fallback=existing)
        try:
            daily_meal = daily_meal_service.update(
                user_id=request.user.id, daily_meal_id=daily_meal_id, **fields
            )
        except MealPlanNotOwnedError:
            raise PermissionDenied("You do not own this meal plan.")
        return Response(DailyMealSerializer(daily_meal).data)

    @staticmethod
    def _parse_daily_meal_id(pk):
        try:
            return int(pk)
        except (TypeError, ValueError):
            return None

    def _fields_from(self, validated_data, fallback=None):
        meal_plan = validated_data.get("meal_plan")
        meal_plan_id = meal_plan.id if meal_plan else (fallback.meal_plan_id if fallback else None)
        return {
            "meal_plan_id": meal_plan_id,
            "date": validated_data.get("date", fallback.date if fallback else None),
            "meal_type": validated_data.get("meal_type", fallback.meal_type if fallback else None),
            "food_ids": (
                [food.id for food in validated_data["food_ids"]]
                if "food_ids" in validated_data
                else [food.id for food in fallback.foods]
            ),
            "notes": validated_data.get("notes", fallback.notes if fallback else ""),
        }


class MealSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MealSuggestion.objects.all()
    serializer_class = MealSuggestionSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def by_meal_type(self, request):
        """Get suggestions filtered by meal type"""
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
        meal_plan_id = self.request.query_params.get("meal_plan")
        return meal_settings_service.list_for_user(
            self.request.user.id,
            meal_plan_id=int(meal_plan_id) if meal_plan_id else None,
        )
