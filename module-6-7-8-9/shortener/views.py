import logging

from core.permissions import IsOwnerOrReadOnly
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import URL
from .serializers import URLSerializer
from .tasks import fetch_and_save_metadata_task, track_click_task
from .utils import generate_short_code

logger = logging.getLogger(__name__)


class URLPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class URLCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["URLs"],
        summary="List User URLs",
        description="Retrieve a paginated list of URLs owned by the authenticated user. Pass a ?tag= query parameter to filter.",
        responses=URLSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="tag",
                description="Filter URLs by tag name",
                required=False,
                type=str,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        urls = request.user.url_set.all().order_by("-created_at")
        tag = request.query_params.get("tag")
        if tag:
            urls = urls.filter(tags__name=tag)

        paginator = URLPagination()
        result_page = paginator.paginate_queryset(urls, request, view=self)
        serializer = URLSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["URLs"],
        summary="Create Short URL",
        description="Create a new short URL. Premium users can specify a custom alias.",
        request=URLSerializer,
        responses=URLSerializer,
    )
    def post(self, request, *args, **kwargs):
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

            custom_alias = serializer.validated_data.get("custom_alias")

            if custom_alias:
                # If custom alias is provided (Premium only check passed above), use it
                url_instance = serializer.save(
                    short_code=custom_alias, owner=request.user
                )
            else:
                # Otherwise generate a random code
                code = generate_short_code()
                while URL.objects.filter(short_code=code).exists():
                    code = generate_short_code()
                url_instance = serializer.save(short_code=code, owner=request.user)

            # Fire off the async task to fetch metadata
            fetch_and_save_metadata_task.delay(url_instance.short_code)

            logger.info(
                "Short URL created",
                extra={
                    "short_code": url_instance.short_code,
                    "user_id": request.user.id,
                    "is_premium_alias": bool(custom_alias),
                },
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If invalid, return errors
        logger.warning(
            "Failed to create URL due to validation errors",
            extra={"errors": serializer.errors, "user_id": request.user.id},
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLRedirectView(APIView):
    @extend_schema(
        tags=["Redirection"],
        summary="Redirect Short Code",
        description="Redirect a short code to its original target URL and track the click event asynchronously.",
        responses={302: None, 410: dict},
    )
    def get(self, request, short_code, *args, **kwargs):
        # 1. Attempt to get from cache
        target_url = cache.get(f"url:{short_code}")

        if not target_url:
            # Cache Miss: Fetch from DB and Cache
            from django.utils import timezone

            url = get_object_or_404(URL, short_code=short_code)

            if not url.is_active:
                logger.warning(
                    "Attempted to access inactive URL", extra={"short_code": short_code}
                )
                return Response(
                    {"error": "This URL is inactive."}, status=status.HTTP_410_GONE
                )

            if url.expires_at and timezone.now() > url.expires_at:
                logger.warning(
                    "Attempted to access expired URL", extra={"short_code": short_code}
                )
                return Response(
                    {"error": "This URL has expired."}, status=status.HTTP_410_GONE
                )

            target_url = url.original_url

            # Calculate cache timeout to respect expiration
            timeout = 3600
            if url.expires_at:
                seconds_to_expire = int(
                    (url.expires_at - timezone.now()).total_seconds()
                )
                timeout = min(timeout, seconds_to_expire)

            if timeout > 0:
                cache.set(f"url:{short_code}", target_url, timeout=timeout)

        # 2. Track Click (Async). Perform the task asynchronously to keep the redirect fast.
        ip = request.META.get("REMOTE_ADDR")
        agent = request.META.get("HTTP_USER_AGENT", "")

        track_click_task.delay(short_code, ip, agent)

        return redirect(target_url)


class URLDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, short_code):
        obj = get_object_or_404(URL, short_code=short_code)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["URLs"],
        summary="Retrieve URL Details",
        description="Fetch details of a specific URL. Requires ownership.",
        responses=URLSerializer,
    )
    def get(self, request, short_code, *args, **kwargs):
        url = self.get_object(short_code)
        serializer = URLSerializer(url)
        return Response(serializer.data)

    @extend_schema(
        tags=["URLs"],
        summary="Update URL",
        description="Update an existing URL. Triggers a background metadata refresh if the target changes.",
        request=URLSerializer,
        responses=URLSerializer,
    )
    def put(self, request, short_code, *args, **kwargs):
        url = self.get_object(short_code)
        old_url = url.original_url

        serializer = URLSerializer(url, data=request.data, partial=True)
        if serializer.is_valid():
            updated_url = serializer.save()

            # If the target URL changed, re-fetch metadata in the background
            if updated_url.original_url != old_url:
                fetch_and_save_metadata_task.delay(updated_url.short_code)

            # Invalidate Cache
            cache.delete(f"url:{short_code}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["URLs"],
        summary="Delete URL",
        description="Hard delete a URL record based on its short code.",
        responses={204: None},
    )
    def delete(self, request, short_code, *args, **kwargs):
        url = self.get_object(short_code)
        url.delete()
        # Invalidate Cache
        cache.delete(f"url:{short_code}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class URLAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, short_code):
        obj = get_object_or_404(URL, short_code=short_code)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["Analytics"],
        summary="Get URL Analytics",
        description="Retrieve click analytics for a specific URL. Premium users receive complete time-series and geographic breakdown.",
        responses={200: dict},
    )
    def get(self, request, short_code, *args, **kwargs):
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        url = self.get_object(short_code)

        # Base analytics for all tiers
        analytics = {
            "total_clicks": url.click_count,
            "created_at": url.created_at,
        }

        # Premium Tier gets expanded metrics
        if request.user.tier == "Premium":
            clicks = url.clicks.all()

            # 1. Geo-Location Breakdown
            locations = (
                clicks.values("country").annotate(count=Count("id")).order_by("-count")
            )
            analytics["locations"] = list(locations)

            # 2. Time-Series Breakdown (Clicks per day)
            time_series = (
                clicks.annotate(date=TruncDate("clicked_at"))
                .values("date")
                .annotate(count=Count("id"))
                .order_by("date")
            )
            # Format datetime dates to string for JSON serialization
            analytics["time_series"] = [
                {
                    "date": entry["date"].strftime("%Y-%m-%d")
                    if entry["date"]
                    else None,
                    "count": entry["count"],
                }
                for entry in time_series
            ]

        return Response(analytics)
