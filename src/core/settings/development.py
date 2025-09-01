from .base import *  # noqa

# Import settings from base.py

# GENERAL
# ------------------------------------------------------------------------------
# In development, we allow all hosts. In production, this will be strictly controlled.
ALLOWED_HOSTS = ["*"]

# DJANGO-DEBUG-TOOLBAR (OPTIONAL BUT RECOMMENDED)
# ------------------------------------------------------------------------------
# To install: uv pip install django-debug-toolbar
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["127.0.0.1"]

# Any other development-specific settings can go here.
# For example, you might want to configure email to print to the console instead of sending.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

logger.info("LOADING DEVELOPMENT SETTINGS")
