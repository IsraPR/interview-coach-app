from .base import *

# Production settings - environment variables should be set by deployment system
# No .env file reading in production

# Production overrides
DEBUG = False
SECRET_KEY = env("SECRET_KEY")  # Must be set in production environment

# Security settings for production
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Allowed hosts should be set properly in production
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Production logging level
logger.remove()
logger.add(sys.stderr, level=env("LOG_LEVEL", default="INFO"))

# AWS Production Configuration
# In production, you might use IAM roles instead of access keys
# If using IAM roles, omit AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# AWS_ACCESS_KEY_ID = None  # Will use IAM role
# AWS_SECRET_ACCESS_KEY = None  # Will use IAM role

# Production AWS service settings
AWS_S3_BUCKET_NAME = env("AWS_S3_BUCKET_NAME")  # Required in production
AWS_TRANSCRIBE_BUCKET = env(
    "AWS_TRANSCRIBE_BUCKET", default=AWS_S3_BUCKET_NAME
)

# Additional production settings can be added here:
# - Static files configuration (S3, CloudFront)
# - Email configuration
# - Caching configuration
# - Database connection pooling
