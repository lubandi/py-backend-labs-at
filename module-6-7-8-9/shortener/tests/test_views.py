from unittest.mock import patch

from core.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shortener.models import URL


class URLAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="freeuser",
            email="free@example.com",
            password="testpassword",
            tier="Free",
        )
        self.premium_user = User.objects.create_user(
            username="premiumuser",
            email="premium@example.com",
            password="testpassword",
            tier="Premium",
        )

        self.url = URL.objects.create(
            original_url="https://example.com/free", short_code="free1", owner=self.user
        )
        self.premium_url = URL.objects.create(
            original_url="https://example.com/prem",
            short_code="prem1",
            owner=self.premium_user,
        )

        # Authenticate natively bypassing token throttles
        self.client.force_authenticate(user=self.user)

    @patch("shortener.views.fetch_and_save_metadata_task.delay")
    def test_create_url_free_tier(self, mock_task):
        url = reverse("url-create", kwargs={"version": "v1"})
        data = {"original_url": "https://google.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(URL.objects.filter(original_url="https://google.com").exists())
        mock_task.assert_called_once()

    def test_create_custom_alias_free_tier(self):
        url = reverse("url-create", kwargs={"version": "v1"})
        data = {"original_url": "https://google.com", "custom_alias": "mygoogle"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("shortener.views.fetch_and_save_metadata_task.delay")
    def test_create_custom_alias_premium_tier(self, mock_task):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse("url-create", kwargs={"version": "v1"})
        data = {"original_url": "https://google.com", "custom_alias": "mygoogle"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["short_code"], "mygoogle")

    def test_list_urls(self):
        url = reverse("url-create", kwargs={"version": "v1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return URLs for the authenticated user (self.user)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_url_detail(self):
        url = reverse(
            "url-detail", kwargs={"version": "v1", "short_code": self.url.short_code}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["original_url"], "https://example.com/free")

    @patch("shortener.views.fetch_and_save_metadata_task.delay")
    def test_update_url(self, mock_task):
        url = reverse(
            "url-detail", kwargs={"version": "v1", "short_code": self.url.short_code}
        )
        data = {"original_url": "https://example.org/updated"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["original_url"], "https://example.org/updated")
        mock_task.assert_called_once()

    def test_delete_url(self):
        url = reverse(
            "url-detail", kwargs={"version": "v1", "short_code": self.url.short_code}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(URL.objects.filter(short_code=self.url.short_code).exists())

    def test_analytics_view_free_tier(self):
        url = reverse(
            "url-analytics", kwargs={"version": "v1", "short_code": self.url.short_code}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_clicks", response.data)
        self.assertNotIn("locations", response.data)

    def test_analytics_view_premium_tier(self):
        self.client.force_authenticate(user=self.premium_user)
        url = reverse(
            "url-analytics",
            kwargs={"version": "v1", "short_code": self.premium_url.short_code},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_clicks", response.data)
        self.assertIn("locations", response.data)
        self.assertIn("time_series", response.data)
