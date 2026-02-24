from core.models import User
from django.test import TestCase
from shortener.models import URL, Click, Tag


class URLModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.url = URL.objects.create(
            original_url="https://example.com",
            short_code="exmpl",
            owner=self.user,
        )

    def test_url_creation(self):
        self.assertEqual(self.url.original_url, "https://example.com")
        self.assertEqual(self.url.short_code, "exmpl")
        self.assertEqual(self.url.owner, self.user)
        self.assertTrue(self.url.is_active)
        self.assertIsNone(self.url.expires_at)

    def test_click_count_default(self):
        self.assertEqual(self.url.click_count, 0)


class TagModelTest(TestCase):
    def test_tag_creation(self):
        tag = Tag.objects.create(name="python")
        self.assertEqual(str(tag), "python")


class ClickModelTest(TestCase):
    def test_click_creation(self):
        user = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpassword"
        )
        url = URL.objects.create(
            original_url="https://example.com", short_code="exmpl2", owner=user
        )
        click = Click.objects.create(url=url, ip_address="192.168.1.1", country="US")
        self.assertEqual(click.url, url)
        self.assertEqual(click.ip_address, "192.168.1.1")
        self.assertEqual(click.country, "US")
