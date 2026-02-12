from django.shortcuts import get_object_or_404, redirect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import URL
from .serializers import URLSerializer
from .utils import generate_short_code


class URLCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=URLSerializer, responses=URLSerializer)
    def post(self, request):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            # TIER CHECK: Free users max 10 URLs
            if request.user.tier == "Free":
                if request.user.url_set.count() >= 10:
                    return Response(
                        {
                            "error": "Free tier limit reached. Upgrade to Premium for unlimited URLs."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                # TIER CHECK: Free users cannot set custom aliases
                if serializer.validated_data.get("custom_alias"):
                    return Response(
                        {"error": "Custom aliases are a Premium feature."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            code = generate_short_code()
            while URL.objects.filter(short_code=code).exists():
                code = generate_short_code()

            # Save the new URL object with the generated code and owner
            serializer.save(short_code=code, owner=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLRedirectView(APIView):
    def get(self, request, short_code):
        url = get_object_or_404(URL, short_code=short_code)
        return redirect(url.original_url)
