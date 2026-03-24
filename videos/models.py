"""Data model for the Video entity including HLS processing state."""

from django.db import models


class Video(models.Model):
    """
    Represents a video in the Videoflix library.

    After upload, a background worker converts the video to HLS format
    in three resolutions using FFMPEG. The hls_ready flag becomes True
    once streaming segments are available.
    """

    CATEGORY_CHOICES = [
        ('action', 'Action'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
        ('romance', 'Romance'),
        ('scifi', 'Science-Fiction'),
        ('documentary', 'Documentary'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='drama',
    )
    video_file = models.FileField(upload_to='videos/originals/')
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    hls_ready = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        """Return the video title as its string representation."""
        return self.title