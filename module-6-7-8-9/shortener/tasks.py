from celery import shared_task
from django.db.models import F

from .models import URL, Click
from .services import fetch_url_metadata


@shared_task
def fetch_and_save_metadata_task(url_short_code):
    """
    Async task to fetch open graph metadata from the Preview service
    and update the URL record.
    """
    try:
        url = URL.objects.get(short_code=url_short_code)
        metadata = fetch_url_metadata(url.original_url)

        if metadata:
            # Update the URL fields with the fetched metadata
            url.title = metadata.get("title") or ""
            url.description = metadata.get("description") or ""
            url.favicon = metadata.get("favicon") or ""
            url.save(update_fields=["title", "description", "favicon"])
    except URL.DoesNotExist:
        pass


@shared_task
def track_click_task(url_short_code, ip_address, user_agent):
    """
    Async task to update click count and create a Click record.
    """
    try:
        url = URL.objects.get(short_code=url_short_code)

        # Update count atomically
        url.click_count = F("click_count") + 1
        url.save()

        # Create detailed click record
        Click.objects.create(url=url, ip_address=ip_address, user_agent=user_agent)
    except URL.DoesNotExist:
        # URL might have been deleted before task ran
        pass


@shared_task
def archive_expired_urls():
    """
    Periodic task to deactivate expired URLs.
    """
    from django.utils import timezone

    expired_urls = URL.objects.filter(is_active=True, expires_at__lt=timezone.now())

    # Bulk update/Deactivate
    count = expired_urls.update(is_active=False)

    return f"Deactivated {count} expired URLs."
