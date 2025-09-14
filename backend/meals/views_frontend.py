from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os

def index(request):
    """Serve the React app"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for Heroku"""
    return JsonResponse({"status": "healthy", "message": "Meal Planner API is running"})
