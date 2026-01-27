from django.shortcuts import redirect
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ShortURLCreateSerializer, ShortURLResponseSerializer
from .services import UrlShortenerService


class ShortenViewSet(viewsets.ViewSet):
    """
    ViewSet for creating short URLs.
    """

    def create(self, request):
        serializer = ShortURLCreateSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            short_url_instance = UrlShortenerService.shorten_url(url)

            response_serializer = ShortURLResponseSerializer(
                short_url_instance, context={"request": request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectView(APIView):
    """
    Redirect to the original URL.
    """

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

    def retrieve(self, request, pk=None):
        # 'pk' here is the short_code
        instance = UrlShortenerService.get_stats(pk)
        if instance:
            serializer = ShortURLResponseSerializer(
                instance, context={"request": request}
            )
            return Response(serializer.data)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
