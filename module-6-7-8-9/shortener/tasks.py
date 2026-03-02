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
            return {
                "action": "metadata_fetched",
                "short_code": url_short_code,
                "status": "success",
                "title": url.title,
            }
        return {
            "action": "metadata_fetched",
            "short_code": url_short_code,
            "status": "failed",
            "reason": "No metadata found",
        }
    except URL.DoesNotExist:
        return {
            "action": "metadata_fetched",
            "short_code": url_short_code,
            "status": "error",
            "reason": "URL not found",
        }


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
        click = Click(url=url, ip_address=ip_address, user_agent=user_agent)

        # Default fallback values for GeoIP
        click.country = "Unknown"
        click.city = "Unknown"

        click.save()

        if ip_address and ip_address not in ("127.0.0.1", "localhost", "::1"):
            # Defer GeoIP fetching to a dedicated, rate-limited background task
            fetch_geoip_for_click.delay(click.id, ip_address)

        return {
            "action": "click_tracked",
            "short_code": url_short_code,
            "ip": ip_address,
        }
    except URL.DoesNotExist:
        # URL might have been deleted before task ran
        return {
            "action": "click_tracked",
            "short_code": url_short_code,
            "status": "error",
            "reason": "URL not found",
        }


@shared_task(rate_limit="40/m")
def fetch_geoip_for_click(click_id, ip_address):
    """
    Dedicated task to fetch GeoIP data for a click.
    Rate limited to 40 per minute to respect free API tiers (ip-api.com allows 45/m).
    """
    import httpx

    try:
        click = Click.objects.get(id=click_id)
        response = httpx.get(f"http://ip-api.com/json/{ip_address}", timeout=10.0)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                click.country = data.get("country") or "Unknown"
                click.city = data.get("city") or "Unknown"
                click.save(update_fields=["country", "city"])

        return {"action": "geoip_fetched", "click_id": click_id, "status": "success"}
    except (Click.DoesNotExist, httpx.RequestError) as e:
        return {
            "action": "geoip_fetched",
            "click_id": click_id,
            "status": "failed",
            "error": str(e),
        }


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
