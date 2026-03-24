"""Serializers for the videos app."""

from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.

    Returns video metadata with an absolute thumbnail URL
    ready for use in the frontend.
    """

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'created_at', 'title',
            'description', 'thumbnail_url', 'category',
        ]

    def get_thumbnail_url(self, obj):
        """
        Return the absolute URL for the video's thumbnail image.

        Args:
            obj (Video): The Video instance being serialized.

        Returns:
            str | None: Absolute thumbnail URL, or None if no thumbnail.
        """
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None