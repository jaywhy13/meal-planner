from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
from .views import (
    DailyMealViewSet,
    FoodViewSet,
    MealPlanViewSet,
    MealSettingsViewSet,
    MealSuggestionViewSet,
)

router.register(r"meal-plans", MealPlanViewSet)
router.register(r"foods", FoodViewSet)
router.register(r"daily-meals", DailyMealViewSet)
router.register(r"meal-suggestions", MealSuggestionViewSet)
router.register(r"meal-settings", MealSettingsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
