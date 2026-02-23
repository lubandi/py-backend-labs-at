from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class ExtractMetadataViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.extract_url = reverse("extract_metadata")

    def test_missing_url(self):
        response = self.client.post(self.extract_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    @patch("extractor.views.httpx.get")
    def test_valid_extraction(self, mock_get):
        # Mock successful HTML response
        class MockResponse:
            def __init__(self, text, status_code):
                self.text = text
                self.status_code = status_code

            def raise_for_status(self):
                pass

        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="This is a test description.">
                <link rel="icon" href="https://example.com/favicon.ico">
            </head>
            <body></body>
        </html>
        """
        mock_get.return_value = MockResponse(html_content, 200)

        response = self.client.post(
            self.extract_url, {"url": "https://example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Page")
        self.assertEqual(response.data["description"], "This is a test description.")
        self.assertEqual(response.data["favicon"], "https://example.com/favicon.ico")

    @patch("extractor.views.httpx.get")
    def test_fetch_error(self, mock_get):
        import httpx

        mock_get.side_effect = httpx.RequestError("Connection timeout", request=None)

        response = self.client.post(
            self.extract_url, {"url": "https://example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Failed to fetch URL", response.data["error"])
