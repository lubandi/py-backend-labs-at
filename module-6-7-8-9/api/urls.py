from core.views import CustomTokenObtainPairView, HealthCheckView, UserRegistrationView
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from shortener.views import URLCreateView, URLDetailView

urlpatterns = [
    path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("urls/", URLCreateView.as_view(), name="url-create"),
    path("urls/<str:short_code>/", URLDetailView.as_view(), name="url-detail"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
]
