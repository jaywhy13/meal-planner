"""
AWS Lambda handler for Django application using Mangum.

Supports two invocation modes:
  1. HTTP requests — forwarded to Django via Mangum (normal Lambda URL traffic)
  2. Management commands — invoke the Lambda directly with a JSON payload:
       {"management_command": "migrate"}
       {"management_command": "populate_data"}
       {"management_command": "migrate", "args": ["--run-syncdb"]}
"""

import os
from io import StringIO

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
from django.core.management import call_command

application = get_asgi_application()

print("Creating the handler now...")

# Mangum translates Lambda HTTP events into ASGI requests for Django
http_handler = Mangum(application, lifespan="off")

print("Handler created successfully.")


def management_command_handler(event, context):
    command = event["management_command"]
    args = event.get("args", [])

    stdout = StringIO()
    stderr = StringIO()
    try:
        call_command(command, *args, stdout=stdout, stderr=stderr)
        return {
            "success": True,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
        }


def handler(event, context):
    if "management_command" in event:
        return management_command_handler(event, context)
    return http_handler(event, context)
