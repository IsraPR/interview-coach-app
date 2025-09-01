from typing import Dict, List, Any, Tuple
from django.http import JsonResponse, HttpRequest
from ninja.errors import ValidationError as NinjaValidationError


class BaseException(Exception):
    """Base custom exception"""

    def __init__(self, msg: str = "Server error", *args):
        super().__init__(*args)
        self.msg = msg


class InternalServerError(BaseException):
    def __init__(
        self, msg: str = "Internal server error", *args: Tuple[Any, Any]
    ):
        super().__init__(msg=msg, *args)
        self.msg = msg


class BadRequestException(BaseException):
    """Custom bad request"""

    def __init__(
        self,
        msg: str = "Bad request",
        code: str = "bad_request_error",
        *args: Tuple[Any, Any],
    ):
        super().__init__(msg=msg, *args)
        self.msg = msg
        self.code = code


def format_validation_errors(errors: List[Dict[str, Any]]) -> Dict[str, str]:
    """Convert Ninja validation errors to a flat dict with dotted paths"""
    details = {}
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"])
        details[field] = error["msg"]
    return details


def validation_error_handler(
    request: HttpRequest, exc: NinjaValidationError
) -> JsonResponse:
    """Custom handler for request validation errors"""
    formatted = {
        "message": "Bad request",
        "error": {
            "message": "Invalid input data",
            "code": "input_data_error",
            "details": format_validation_errors(exc.errors),
        },
    }
    return JsonResponse(formatted, status=400)


def bad_request_handler(
    request: HttpRequest, exc: BadRequestException
) -> JsonResponse:
    """Custom handler for bad request errors"""
    formatted = {
        "message": "Bad request",
        "error": {
            "message": exc.msg,
            "code": exc.code if exc.code else "bad_request_error",
        },
    }
    return JsonResponse(formatted, status=400)


def internal_server_error_handler(
    request: HttpRequest, exc: InternalServerError
) -> JsonResponse:
    """Custom handler for internal server errors"""
    formatted = {"error": exc.msg}
    return JsonResponse(formatted, status=500)
