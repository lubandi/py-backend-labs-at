from django.db import models
from django.utils import timezone


class URLManager(models.Manager):
    def active_urls(self):
        """
        Returns URLs that are set to active and have not expired.
        """
        now = timezone.now()
        # Filter 1: is_active=True
        # Filter 2: expires_at is None OR expires_at is in the future
        return self.filter(is_active=True).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )

    def expired_urls(self):
        """
        Returns URLs that satisfy the expiration condition.
        """
        now = timezone.now()
        return self.filter(expires_at__lte=now)

    def popular_urls(self, n=10):
        """
        Returns the top N most visited URLs.
        """
        return self.order_by("-click_count")[:n]

    def with_tags(self):
        """
        Optimizes fetching of tags (ManyToMany) to avoid N+1 problems.
        """
        return self.prefetch_related("tags")

    def with_owner(self):
        """
        Optimizes fetching of owner (ForeignKey) to avoid N+1 problems.
        """
        return self.select_related("owner")

    def with_all_info(self):
        """
        Optimizes fetching of all related data (tags + owner).
        """
        return self.select_related("owner").prefetch_related("tags")


class ClickManager(models.Manager):
    def clicks_per_country(self, url_id):
        """Aggregates clicks by country basing on a specific URL using annotate."""

        return (
            self.filter(url_id=url_id)
            .values("country")
            .annotate(total=models.Count("id"))
            .order_by("-total")
        )
