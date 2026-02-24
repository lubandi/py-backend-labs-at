from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import URL, Tag


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Minimal Payload (Free User)",
            summary="Basic URL Creation",
            description="A clean, default payload just requiring the original destination.",
            value={"original_url": "https://www.example.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Advanced Payload (Premium User)",
            summary="Custom Alias & Expiry",
            description="Create a URL with custom tags, alias, and explicit expiration date.",
            value={
                "original_url": "https://www.example.com",
                "custom_alias": "mycampaign",
                "tags": ["marketing", "newsletter"],
                "expires_at": "2026-12-31T23:59:59Z",
            },
            request_only=True,
        ),
    ]
)
class URLSerializer(serializers.ModelSerializer):
    custom_alias = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default=None,
        help_text="Optional custom alphanumeric alias",
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
        default=list,
        help_text="List of tag names from Work, Personal, Newsletter, Social, Marketing",
        write_only=True,
    )

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
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_custom_alias(self, value):
        if value == "":
            return None
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert tag objects to list of strings
        representation["tags"] = [tag.name for tag in instance.tags.all()]
        return representation

    def create(self, validated_data):
        from datetime import timedelta

        from django.utils import timezone

        tags_data = validated_data.pop("tags", [])

        # Default expiry to 6 months (180 days) if not explicitly provided
        if "expires_at" not in validated_data or not validated_data["expires_at"]:
            validated_data["expires_at"] = timezone.now() + timedelta(days=180)

        url = super().create(validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            url.tags.add(tag)
        return url

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        url = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return url
