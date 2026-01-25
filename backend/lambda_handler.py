"""
AWS Lambda handler for Django application using Mangum
"""

import os

import django
from mangum import Mangum

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meal_planner.settings_lambda")

print("Initializing Django...")

# Initialize Django
django.setup()

print("Django initialized.")

# Get the WSGI application
from django.core.asgi import get_asgi_application

application = get_asgi_application()

print("Creating the handler now...")

# Create Mangum handler for Lambda
handler = Mangum(application, lifespan="off")

print("Handler created successfully.")
