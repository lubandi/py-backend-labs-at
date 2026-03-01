import ipaddress
import socket
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import httpx
import pybreaker
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# In-memory dictionary for keeping a Circuit Breaker per target domain
# Fails after 3 consecutive errors, resets after 60 seconds.
domain_breakers = defaultdict(
    lambda: pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)
)


def is_safe_url(url: str) -> bool:
    """Verifies that the URL's resolved IP is not a private, loopback, or reserved address."""
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        if not hostname:
            return False

        # Resolve hostname to IP
        ip_address_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_address_str)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        ):
            return False

        return True
    except (socket.gaierror, ValueError):
        # If we can't resolve the hostname or parse the IP, fail securely
        return False


def get_domain_breaker(url: str):
    domain = urlparse(url).netloc
    return domain_breakers[domain]


# Retry up to 3 times, with exponential backoff (2s, 4s, 8s)
# Only try again if it's a network error or a 5xx Server error.
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    reraise=True,
)
def fetch_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    breaker = get_domain_breaker(url)

    # Wrap the actual HTTP call with the circuit breaker
    @breaker
    def _execute_request():
        response = httpx.get(url, timeout=10.0, follow_redirects=True, headers=headers)
        # Only raise and trigger circuit breaker/retries for 5xx Server Errors
        # 4xx Client Errors (like 404 Not Found) should just be returned as failed fetches
        if response.status_code >= 500:
            response.raise_for_status()
        return response

    return _execute_request()


def extract_url_metadata(url: str) -> dict:
    """
    Fetches the URL and extracts title, description, and favicon.
    Returns a dict with 'title', 'description', 'favicon'.
    Raises Exception if the fetch fails or circuit breaker is open.
    """
    if not is_safe_url(url):
        raise ValueError("Invalid or unsafe URL provided (SSRF Protection)")

    response = fetch_url(url)
    response.raise_for_status()  # Catch 4xx errors here to raise Exception without tripping the breaker

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract Title
    title_tag = soup.find("title")
    title = title_tag.string.strip() if title_tag and title_tag.string else None

    # Extract Description
    description = None
    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    if meta_desc:
        description = meta_desc.get("content", "").strip()

    # Extract Favicon
    favicon = None
    icon_link = soup.find("link", rel=lambda x: x and "icon" in x)
    if icon_link:
        favicon = icon_link.get("href")
        if favicon and not favicon.startswith("http"):
            favicon = urljoin(url, favicon)

    return {"title": title, "description": description, "favicon": favicon}
