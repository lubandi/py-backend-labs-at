from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup


def extract_url_metadata(url: str) -> dict:
    """
    Fetches the URL and extracts title, description, and favicon.
    Returns a dict with 'title', 'description', 'favicon'.
    Raises Exception if the fetch fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = httpx.get(url, timeout=5.0, follow_redirects=True, headers=headers)
    response.raise_for_status()

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
