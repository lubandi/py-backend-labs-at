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
    throttle_classes = (
        []
    )  # you don't want to throttle health endpoints. health-check endpoints shouldn't be rate-limited (otherwise load balancers might think the server is down if they check too frequently).

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
            from redis.exceptions import RedisError

            con = get_redis_connection("default")
            con.ping()
            health_status["services"]["redis"] = "healthy"
        except RedisError:
            health_status["services"]["redis"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception:
            health_status["services"]["redis"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        # Check Celery
        try:
            from config.celery import app as celery_app

            inspector = celery_app.control.inspect(timeout=1.0)
            availability = inspector.ping()
            if availability:
                health_status["services"]["celery"] = "healthy"
            else:
                health_status["services"]["celery"] = "unhealthy"
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception:
            health_status["services"]["celery"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        # Check Preview Service
        try:
            import httpx
            from django.conf import settings

            preview_url = getattr(
                settings, "PREVIEW_SERVICE_URL", "http://preview-service:8001/extract/"
            )
            response = httpx.options(preview_url, timeout=2.0)
            # 200 OK, 204 No Content, or 405 Method Not Allowed mean it's responding
            if response.status_code in [200, 204, 405, 400]:
                health_status["services"]["preview"] = "healthy"
            else:
                health_status["services"]["preview"] = "unhealthy"
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception:
            health_status["services"]["preview"] = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        if status_code != status.HTTP_200_OK:
            health_status["status"] = "unhealthy"

        return Response(health_status, status=status_code)
