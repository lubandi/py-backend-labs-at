import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Custom Exception Classes
# ---------------------------------------------------------


class BaseCustomException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred."
    default_code = "internal_server_error"


class ServiceUnavailableException(BaseCustomException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service is temporarily unavailable. Please try again later."
    default_code = "service_unavailable"


class TierLimitExceededException(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Free tier limit reached. Please upgrade to Premium."
    default_code = "tier_limit_exceeded"


class PremiumFeatureException(BaseCustomException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "This feature is only available to Premium members."
    default_code = "premium_feature_required"


class InvalidURLException(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided URL is invalid or unsafe."
    default_code = "invalid_url"


# ---------------------------------------------------------
# Custom Exception Handler
# ---------------------------------------------------------


def custom_exception_handler(exc, context):
    """
    Custom exception handler that standardizes response formats.
    It catches DRF exceptions and custom exceptions to return a standard dictionary:
    {
        "error": {
            "code": "error_code",
            "message": "Human readable message",
            "details": {} # Optional field for validation errors
        }
    }
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now standardize the response format.
    if response is not None:
        # Log 5xx errors automatically
        if response.status_code >= 500:
            logger.error(f"Server Error ({response.status_code}): {exc}")

        # Standard DRF Exceptions usually return a dict or string in response.data
        formatted_data = {
            "error": {
                "message": "",
                "code": getattr(
                    exc, "get_codes", lambda: getattr(exc, "default_code", "error")
                )(),
            }
        }

        # If it's a validation error (like from serializers), response.data is often a dict of fields -> lists of errors
        if isinstance(response.data, dict) and "detail" not in response.data:
            formatted_data["error"]["message"] = "Validation Error"
            formatted_data["error"]["code"] = "validation_error"
            formatted_data["error"]["details"] = response.data
        else:
            # Otherwise, use the 'detail' provided by the exception
            detail = response.data.get("detail", str(exc))
            formatted_data["error"]["message"] = detail

            # If standard DRF provided a code like {"detail": "...", "code": "..."} we can optionally extract it,
            # but usually `get_codes()` on the exception class is best.

        response.data = formatted_data

    return response
