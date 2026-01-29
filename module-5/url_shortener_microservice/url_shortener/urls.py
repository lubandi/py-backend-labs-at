from django.urls import path, re_path

from .views import AnalyticsViewSet, RedirectView, ShortenViewSet

urlpatterns = [
    path(
        "api/shorten/", ShortenViewSet.as_view({"post": "create"}), name="shorten_url"
    ),
    path(
        "api/stats/<str:short_code>/",
        AnalyticsViewSet.as_view({"get": "retrieve"}),
        name="url_stats",
    ),
    # only capture 6 length numbers + leter patterns because our codes are that long
    re_path(
        r"^(?P<short_code>[a-zA-Z0-9]{6})$", RedirectView.as_view(), name="redirect_url"
    ),
]
