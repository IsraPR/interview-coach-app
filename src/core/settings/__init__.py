import os

# Determine which settings to use based on environment
DJANGO_ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "development")

if DJANGO_ENVIRONMENT == "production":
    from .production import *
elif DJANGO_ENVIRONMENT == "docker":
    from .docker import *
else:
    from .development import *
