from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserRegistrationSerializer


@extend_schema_view(post=extend_schema(tags=["Auth"], summary="Register New User"))
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "User registered successfully."}, status=status.HTTP_201_CREATED
        )


@extend_schema_view(post=extend_schema(tags=["Auth"], summary="Login & Obtain Tokens"))
class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


@extend_schema_view(post=extend_schema(tags=["Auth"], summary="Refresh Access Token"))
class CustomTokenRefreshView(TokenRefreshView):
    pass


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=["Health"], summary="System Health Check")
    def get(self, request, *args, **kwargs):
        health_status = {"status": "ok", "services": {}}
        status_code = status.HTTP_200_OK

        # Check Database
        try:
            from django.db import connections

            connections["default"].cursor()
            health_status["services"]["database"] = "healthy"
        except Exception:
            health_status["services"]["database"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        # Check Redis
        try:
            from django_redis import get_redis_connection

            con = get_redis_connection("default")
            con.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception:
            health_status["services"]["redis"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(health_status, status=status_code)
