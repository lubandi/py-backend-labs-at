import secrets
import string

from django.core.cache import cache
from django.db.models import F

from .models import ShortURL


class UrlShortenerService:
    @staticmethod
    def generate_short_code(length=6):
        """Generate a random short code."""
        chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def shorten_url(original_url: str, custom_code: str = None) -> ShortURL:
        """
        Create a new ShortURL instance.
        If custom_code is provided, try to use it.
        If the URL already exists (and no custom code), return the existing instance (Idempotency).
        """
        # If custom code is provided, we skip the idempotency check for existing URL
        # because the user explicitly wants THIS code for THIS url.
        if custom_code:
            if ShortURL.objects.filter(short_code=custom_code).exists():
                raise ValueError("Custom code already exists.")

            instance = ShortURL.objects.create(
                original_url=original_url, short_code=custom_code
            )
            cache.set(f"short_url:{custom_code}", original_url, timeout=None)
            return instance

        # OPTIMIZATION: Check if this URL is already shortened
        existing = ShortURL.objects.filter(original_url=original_url).first()
        if existing:
            return existing

        while True:
            code = UrlShortenerService.generate_short_code()
            if not ShortURL.objects.filter(short_code=code).exists():
                break

        instance = ShortURL.objects.create(original_url=original_url, short_code=code)

        # Cache the result for fast lookups
        cache.set(f"short_url:{code}", original_url, timeout=None)  # No expiry

        return instance

    @staticmethod
    def get_original_url(short_code: str) -> str:
        """
        Retrieve the original URL from a short code.
        Uses Redis cache for performance.
        Increments click count.
        """
        # Try cache first
        cached_url = cache.get(f"short_url:{short_code}")

        if cached_url:
            # Increment clicks in DB
            ShortURL.objects.filter(short_code=short_code).update(
                clicks=F("clicks") + 1
            )
            return cached_url

        # Fallback to DB
        try:
            instance = ShortURL.objects.get(short_code=short_code)

            # Update cache
            cache.set(f"short_url:{short_code}", instance.original_url, timeout=None)

            # Increment clicks
            instance.clicks = F("clicks") + 1
            instance.save(update_fields=["clicks"])

            return instance.original_url
        except ShortURL.DoesNotExist:
            return None

    @staticmethod
    def get_stats(short_code: str):
        """
        Get statistics for a short code.
        """
        try:
            return ShortURL.objects.get(short_code=short_code)
        except ShortURL.DoesNotExist:
            return None
