from core.views import UserRegistrationView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from shortener.views import URLCreateView

urlpatterns = [
    path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("urls/", URLCreateView.as_view(), name="url-create"),
]
