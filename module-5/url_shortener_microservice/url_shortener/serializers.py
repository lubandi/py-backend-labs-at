from rest_framework import serializers

from .models import ShortURL


class ShortURLCreateSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2000, required=True)


class ShortURLResponseSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = ["original_url", "short_code", "short_url", "created_at", "clicks"]

    def get_short_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/{obj.short_code}")
        return f"/{obj.short_code}"
