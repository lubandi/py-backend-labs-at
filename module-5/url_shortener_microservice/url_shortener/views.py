from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ShortURLCreateSerializer, ShortURLResponseSerializer
from .services import UrlShortenerService


class ShortenViewSet(viewsets.ViewSet):
    """
    ViewSet for creating short URLs.
    """

    @extend_schema(
        request=ShortURLCreateSerializer,
        responses={201: ShortURLResponseSerializer},
        description="Submit a long URL to generate a short code.",
        examples=[
            OpenApiExample(
                "Correct Input",
                value={"url": "https://www.example.com"},
                request_only=True,
            ),
        ],
    )
    def create(self, request):
        serializer = ShortURLCreateSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            custom_code = serializer.validated_data.get("custom_code")

            try:
                short_url_instance = UrlShortenerService.shorten_url(
                    url, custom_code=custom_code
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            response_serializer = ShortURLResponseSerializer(
                short_url_instance, context={"request": request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectView(APIView):
    """
    Redirect to the original URL.
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="short_code",
                location=OpenApiParameter.PATH,
                description="The short code to redirect",
                type=str,
            )
        ],
        responses={302: None, 404: None},
        description="Redirects to the original URL based on the short code.",
    )
    def get(self, request, short_code):
        original_url = UrlShortenerService.get_original_url(short_code)
        if original_url:
            return redirect(original_url)
        return Response(
            {"error": "Short URL not found"}, status=status.HTTP_404_NOT_FOUND
        )


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for retrieving analytics.
    """

    @extend_schema(
        responses={200: ShortURLResponseSerializer},
        description="Get statistics for a specific short code.",
    )
    def retrieve(self, request, short_code=None):
        instance = UrlShortenerService.get_stats(short_code)
        if instance:
            serializer = ShortURLResponseSerializer(
                instance, context={"request": request}
            )
            return Response(serializer.data)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
