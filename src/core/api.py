from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja.errors import ValidationError
from .exceptions import (
    validation_error_handler,
    bad_request_handler,
    BadRequestException,
    InternalServerError,
    internal_server_error_handler,
)
from .schema import CustomTokenObtainPairController
from apps.users.api import router as users_router
from apps.coaching.api import (
    profiles_router,
    profile_sessions_router,
    sessions_router,
)

api = NinjaExtraAPI()
api.register_controllers(CustomTokenObtainPairController)

# Custom exception handling
api.add_exception_handler(ValidationError, validation_error_handler)
api.add_exception_handler(BadRequestException, bad_request_handler)
api.add_exception_handler(InternalServerError, internal_server_error_handler)


api.add_router("/users", users_router)
api.add_router("/coaching/job-profiles", profiles_router, auth=JWTAuth())
api.add_router(
    "/coaching/job-profiles/{profile_id}/sessions",
    profile_sessions_router,
    auth=JWTAuth(),
)
api.add_router("/coaching/sessions", sessions_router, auth=JWTAuth())


@api.get("/health/", summary="Test API Status")
def health_check(request):
    """A simple secured endpoint to test authentication."""
    return {"status": "healthy"}
