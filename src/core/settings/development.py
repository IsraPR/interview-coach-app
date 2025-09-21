from .base import *  # noqa

# Read local environment file
environ.Env.read_env(BASE_DIR / ".env.local")  # noqa

# Development-specific overrides
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# You can add development-specific settings here if needed
# For example:
# - Email backend for testing
# - Additional debugging tools
# - Development-specific middleware
