import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request
        logger.info(f"Incoming Request: {request.method} {request.path}")

        response = self.get_response(request)

        # Log response status
        logger.info(f"Response Status: {response.status_code}")

        return response
