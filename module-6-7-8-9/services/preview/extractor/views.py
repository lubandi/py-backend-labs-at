import httpx
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import URLInputSerializer
from .services import extract_url_metadata


class ExtractMetadataView(APIView):
    def post(self, request):
        serializer = URLInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]

        try:
            metadata = extract_url_metadata(url)
            return Response(metadata)
        except httpx.RequestError as e:
            return Response(
                {"error": f"Failed to fetch URL: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except httpx.HTTPStatusError as e:
            return Response(
                {"error": f"HTTP Error {e.response.status_code}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
