from rest_framework import serializers

from .models import URL


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ["original_url", "short_code", "created_at"]
        read_only_fields = ["short_code", "created_at"]
