from rest_framework import serializers


class URLInputSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
