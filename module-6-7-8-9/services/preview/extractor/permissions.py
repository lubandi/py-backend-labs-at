from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class MicroserviceTokenAuthentication(BaseAuthentication):
    """
    Authenticates requests that include the correct Microservice Token.
    """

    def authenticate(self, request):
        token = request.headers.get("X-Microservice-Token")
        if not token:
            return None  # Fallback to other authentication mechanisms if any

        expected_token = getattr(
            settings, "MICROSERVICE_TOKEN", "local-dev-secret-token"
        )
        if token == expected_token:
            # Return a dummy user and the token
            return (AnonymousUser(), token)

        raise AuthenticationFailed("Invalid Microservice Token")
