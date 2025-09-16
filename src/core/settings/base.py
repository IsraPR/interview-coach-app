"""
Base settings for the AI project.

- Reads environment variables from a .env file.
- Contains all common settings shared across environments.
- Environment-specific settings are in development.py and production.py.
"""

import environ
import sys

from pathlib import Path
from datetime import timedelta
from loguru import logger

# Initialize django-environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: ROOT_DIR / 'subdir'.
# src/core/settings/base.py -> src/ -> /your_ai_project/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

# Attempt to read the .env file, which should be in the project root.
environ.Env.read_env(BASE_DIR / ".env")


# GENERAL
# ------------------------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# As a default, we allow nothing. The development/production settings will override this.
ALLOWED_HOSTS = []


# APPS
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Third Party (server)
    "daphne",
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third Party
    "ninja",
    "channels",
    "ninja_extra",
    "corsheaders",
    # Custom Apps
    "apps.users",
    "apps.interactions",
    "apps.ai_engine",
    "apps.common_models",
    "apps.coaching",
]


# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# URLS
# ------------------------------------------------------------------------------
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"


# ASYNC & CHANNELS
# ------------------------------------------------------------------------------
ASGI_APPLICATION = "core.asgi.application"

REDIS_URL = env("REDIS_URL", default=None)
if REDIS_URL:
    # Production/Full-Stack Local: Use Redis
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Lite Local/Testing: Use in-memory layer
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# DATABASES
# ------------------------------------------------------------------------------
# Reads the DATABASE_URL environment variable.
# Format: postgres://USER:PASSWORD@HOST:PORT/NAME
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True


# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# STATIC FILES
# ------------------------------------------------------------------------------
STATIC_URL = "static/"


# DEFAULT PRIMARY KEY FIELD TYPE
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CELERY SETTINGS
# ------------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=None)

if CELERY_BROKER_URL:
    # Production/Full-Stack Local: Use Redis as the broker
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
else:
    # Lite Local/Testing: Run tasks synchronously in the same process
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 4 * 60

# LOGGING
# ------------------------------------------------------------------------------
# Loguru logger config
# Set level; Use this logger through the api application
logger.remove()
logger.add(sys.stderr, level=env("LOG_LEVEL", default="DEBUG"))


# AWS
# ------------------------------------------------------------------------------
DEFAULT_REGION = env("AWS_REGION", default="us-east-1")
# Bedrock
DEFAULT_AGENT_MODEL_ID = env("AGENT_MODEL_ID", default="amazon.nova-lite-v1:0")
SPEECH_TO_SPEECH_MODEL_ID = env(
    "SPEECH_TO_SPEECH_MODEL_ID", default="amazon.nova-sonic-v1:0"
)

AUTH_USER_MODEL = "users.User"
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),  # Default is 5 min
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # Other options like SIGNING_KEY, etc.
}

# CORS
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
