from ninja import Router
from core.settings.base import logger
from core.exceptions import BadRequestException
from ninja_jwt.authentication import JWTAuth

from .schemas import UserSchema, SignUpSchema
from .services import create_user, UserAlreadyExistsError, get_user

router = Router(tags=["Users"])


@router.post(
    "/signup",
    response={
        201: UserSchema
    },  # On success, return a 201 Created with the user data
    auth=None,  # This endpoint must be public
    summary="Register a new user",
)
def signup(request, payload: SignUpSchema):
    """
    Creates a new user account.

    Returns the created user's public information upon successful registration.
    """
    try:
        user = create_user(payload)
        return 201, user
    except UserAlreadyExistsError as e:
        logger.warning(f"USER_ALREADY_EXIST: {e}")
        raise BadRequestException("User already exist") from e
    except Exception as e:
        logger.error(f"CREATE_USER_ERROR: {e}")
        raise BadRequestException("Error while creating user") from e


@router.get(
    "/profile",
    response={200: UserSchema},
    auth=JWTAuth(),
    summary="Get Current User",
)
def get_current_user(request):
    """Retrieve the profile of the currently authenticated user."""
    return get_user(request.user.id)
