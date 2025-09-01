from django.contrib.auth import get_user_model
from .schemas import SignUpSchema

# Get our custom User model
User = get_user_model()


class UserAlreadyExistsError(ValueError):
    """Custom exception for duplicate user registration."""

    pass


def create_user(payload: SignUpSchema) -> "User":
    """
    Creates a new user in the database.

    Args:
        payload: The validated data from the signup request.

    Returns:
        The newly created User object.

    Raises:
        UserAlreadyExistsError: If a user with the given email already exists.
    """

    # Business Rule: Check if user already exists
    if User.objects.filter(email=payload.email).exists():
        raise UserAlreadyExistsError(
            f"A user with email {payload.email} already exists."
        )

    # Use the custom manager's create_user method to handle password hashing
    user = User.objects.create_user(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    return user


def get_user(user_id: int) -> "User":
    user = User.objects.get(id=user_id)
    return user
