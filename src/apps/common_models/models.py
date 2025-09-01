# src/apps/common_models/models.py
from django.db import models
from django_softdelete.models import SoftDeleteModel


class BaseModel(SoftDeleteModel):
    """
    An abstract base model that provides common fields and functionality.

    All models in the project should inherit from this class.
    It includes:
    - Soft deletion capabilities.
    - `created_at` and `updated_at` timestamp fields.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time when this object was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="The date and time when this object was last updated.",
    )

    class Meta:
        # This makes the model abstract, so it won't create its own DB table.
        abstract = True
        ordering = ["-created_at"]  # Default ordering for all models
