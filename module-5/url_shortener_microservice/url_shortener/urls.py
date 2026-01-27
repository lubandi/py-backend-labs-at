from django.urls import path, re_path

from .views import AnalyticsViewSet, RedirectView, ShortenViewSet

urlpatterns = [
    # API Endpoints
    path(
        "api/shorten/", ShortenViewSet.as_view({"post": "create"}), name="shorten_url"
    ),
    path(
        "api/stats/<str:pk>/",
        AnalyticsViewSet.as_view({"get": "retrieve"}),
        name="url_stats",
    ),
    # Redirect Endpoint (Strict 6-char regex to allow 'admin/', 'api/' etc to fall through)
    re_path(
        r"^(?P<short_code>[a-zA-Z0-9]{6})$", RedirectView.as_view(), name="redirect_url"
    ),
]
