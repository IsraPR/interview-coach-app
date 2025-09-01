from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Defines the admin model for the custom User model.
    """

    # The fields to be displayed in the list view of users
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )

    # The fields that can be used for searching
    search_fields = ("email", "first_name", "last_name")

    # The fields that can be used for filtering
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    # The fields to be displayed when editing a user
    # We group them into fieldsets for a cleaner layout.
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # The fields to be displayed when creating a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "password2"),
            },
        ),
    )

    # Use the email as the ordering field
    ordering = ("email",)

    # Note: Since we removed the 'username' field, we need to tell the admin
    # to use the 'email' field instead for certain operations.
    # The BaseUserAdmin is already configured to handle this when USERNAME_FIELD is set.
