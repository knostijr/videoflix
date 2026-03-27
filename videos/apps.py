"""App configuration for the videos app."""

from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Configuration class for the videos Django application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'

    def ready(self):
        """Import signal handlers when Django has finished loading."""
        import videos.signals  # noqa: F401
