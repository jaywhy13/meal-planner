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
router.register(r"meal-plans", MealPlanViewSet, basename="mealplan")
router.register(r"meals", MealViewSet, basename="meal")
router.register(r"foods", FoodViewSet, basename="food")
router.register(r"daily-meals", DailyMealViewSet, basename="dailymeal")
router.register(r"meal-suggestions", MealSuggestionViewSet, basename="mealsuggestion")
router.register(r"meal-settings", MealSettingsViewSet, basename="mealsettings")

urlpatterns = [
    path("", include(router.urls)),
]
