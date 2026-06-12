from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DailyMealViewSet,
    FoodViewSet,
    MealPlanViewSet,
    MealSettingsViewSet,
    MealSuggestionViewSet,
    MealViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"meal-plans", MealPlanViewSet)
router.register(r"meals", MealViewSet, basename="meal")
router.register(r"foods", FoodViewSet)
router.register(r"daily-meals", DailyMealViewSet)
router.register(r"meal-suggestions", MealSuggestionViewSet)
router.register(r"meal-settings", MealSettingsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
