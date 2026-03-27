"""Django signal handlers for the videos app."""

import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import process_video_to_hls


@receiver(post_save, sender=Video)
def trigger_video_processing(sender, instance, created, **kwargs):
    """
    Enqueue the HLS conversion task when a new video is uploaded.

    Only triggers on creation (created=True), not on subsequent saves
    such as when hls_ready is updated by the worker itself.

    Args:
        sender: The model class sending the signal (Video).
        instance (Video): The saved Video instance.
        created (bool): True only when a new record is created.
        **kwargs: Additional signal keyword arguments.
    """
    if created and instance.video_file:
        queue = django_rq.get_queue('default')
        queue.enqueue(process_video_to_hls, instance.pk)
