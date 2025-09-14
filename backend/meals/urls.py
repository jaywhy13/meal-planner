from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealPlanViewSet, FoodViewSet, DailyMealViewSet, MealSuggestionViewSet, MealSettingsViewSet

router = DefaultRouter()
router.register(r'meal-plans', MealPlanViewSet)
router.register(r'foods', FoodViewSet)
router.register(r'daily-meals', DailyMealViewSet)
router.register(r'meal-suggestions', MealSuggestionViewSet)
router.register(r'meal-settings', MealSettingsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
