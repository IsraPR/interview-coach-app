from .base import *  # noqa

# Read Docker environment file
environ.Env.read_env(BASE_DIR / ".env.docker")  # noqa

# Docker-specific overrides
DEBUG = True
ALLOWED_HOSTS = ["*"]  # More permissive for Docker networking

# Docker typically has more network latency, so increase timeouts if needed
# You can add Docker-specific configurations here if needed
