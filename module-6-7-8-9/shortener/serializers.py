from rest_framework import serializers

from .models import URL


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = [
            "original_url",
            "short_code",
            "custom_alias",
            "title",
            "description",
            "favicon",
            "tags",
            "expires_at",
            "click_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "short_code",
            "title",
            "description",
            "favicon",
            "click_count",
            "created_at",
            "updated_at",
        ]
