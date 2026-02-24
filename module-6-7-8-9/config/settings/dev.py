from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Development-specific settings added here
CORS_ALLOW_ALL_ORIGINS = True
