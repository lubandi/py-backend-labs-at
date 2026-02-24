from django.urls import path

from .views import ExtractMetadataView

urlpatterns = [
    path("extract/", ExtractMetadataView.as_view(), name="extract_metadata"),
]
