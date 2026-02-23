import httpx
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ExtractMetadataView(APIView):
    def post(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Short timeout and User-Agent to prevent 403 Forbidden errors from bot protections
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = httpx.get(
                url, timeout=5.0, follow_redirects=True, headers=headers
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            return Response(
                {"error": f"Failed to fetch URL: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except httpx.HTTPStatusError as e:
            return Response(
                {"error": f"HTTP Error {e.response.status_code}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                from urllib.parse import urljoin

                favicon = urljoin(url, favicon)

        return Response(
            {"title": title, "description": description, "favicon": favicon}
        )
