# src/common/aws/clients.py
import boto3
from functools import lru_cache
from django.conf import settings
from loguru import logger


# --- Cachable Client Factory ---
@lru_cache(maxsize=None)
def get_boto3_client(service_name: str, region_name: str | None = None):
    """
    A cached factory function to get a Boto3 client.
    Using lru_cache ensures we only create one client per service,
    which is efficient and best practice.
    """
    region = region_name or settings.AWS_REGION
    logger.info(
        f"Creating Boto3 client for service='{service_name}' in region='{region}'"
    )

    # In production on ECS, Boto3 will automatically use the IAM role from the task definition.
    # For local dev, it will use the credentials from your .env file.
    return boto3.client(service_name, region_name=region)


# --- Wrapper Instantiation ---
# We can provide pre-configured instances of our wrappers for easy use in other apps.

from .s3 import Bucket
from .bedrock import BedrockRuntime, BedrockAgentRuntime
from .transcribe import Transcribe


def get_s3_bucket(bucket_name: str) -> Bucket:
    """Returns an initialized S3 Bucket wrapper."""
    s3_client = get_boto3_client("s3")
    return Bucket(name=bucket_name, client=s3_client)


def get_bedrock_runtime() -> BedrockRuntime:
    """Returns an initialized BedrockRuntime wrapper."""
    bedrock_client = get_boto3_client("bedrock-runtime")
    return BedrockRuntime(client=bedrock_client)


def get_transcribe_client() -> Transcribe:
    """Returns an initialized Transcribe wrapper."""
    transcribe_client = get_boto3_client("transcribe")
    return Transcribe(client=transcribe_client)
