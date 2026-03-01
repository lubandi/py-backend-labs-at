import httpx
import pybreaker
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import URLInputSerializer
from .services import extract_url_metadata


class ExtractMetadataView(APIView):
    @extend_schema(
        request=URLInputSerializer,
        responses={200: dict, 400: dict},
        summary="Extract metadata from a given URL",
        description="Fetches the title, description, and favicon from the target webpage.",
    )
    def post(self, request, *args, **kwargs):
        serializer = URLInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        url = serializer.validated_data["url"]

        try:
            metadata = extract_url_metadata(url)
            return Response(metadata)
        except pybreaker.CircuitBreakerError:
            from preview.exceptions import CircuitBreakerOpenException

            raise CircuitBreakerOpenException()
        except httpx.RequestError as e:
            from preview.exceptions import TargetNetworkException

            raise TargetNetworkException(
                detail=f"Failed to fetch URL (Network/Timeout): {str(e)}"
            )
        except httpx.HTTPStatusError as e:
            from preview.exceptions import TargetHTTPException

            raise TargetHTTPException(
                detail=f"HTTP Error {e.response.status_code} from target website"
            )
