"""
Lambda-specific Django settings
Inherits from base settings and overrides for AWS Lambda environment
"""

from .settings import *

logging.basicConfig(level=logging.DEBUG)

# Lambda-specific settings

# Allow Lambda function URLs
ALLOWED_HOSTS = ["*"]  # Lambda Function URLs use unique domains


# Security settings for Lambda
SECURE_SSL_REDIRECT = False  # Lambda Function URLs handle SSL
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
APPEND_SLASH = False

# CORS settings - update with your frontend URL
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")


# Logging configuration for CloudWatch
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
