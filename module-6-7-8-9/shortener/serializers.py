from rest_framework import serializers

from .models import URL, Tag


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
        tags_data = validated_data.pop("tags", [])
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
