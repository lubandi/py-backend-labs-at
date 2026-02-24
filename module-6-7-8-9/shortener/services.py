import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_url_metadata(url: str) -> dict:
    """
    Calls the internal Preview Service to extract metadata for a given URL.
    Returns a dict with 'title', 'description', and 'favicon'.
    Returns an empty dict if the service fails or times out.
    """
    preview_url = getattr(
        settings, "PREVIEW_SERVICE_URL", "http://preview-service:8001/extract/"
    )

    try:
        response = httpx.post(
            preview_url,
            json={"url": url},
            timeout=10.0,  # Give the preview service 10 seconds to respond
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(
                f"Preview service returned {response.status_code} for URL {url}: {response.text}"
            )
    except httpx.RequestError as exc:
        logger.error(f"Error calling preview service for {url}: {exc}")
    except Exception as exc:
        logger.error(f"Unexpected error calling preview service for {url}: {exc}")

    return {}
