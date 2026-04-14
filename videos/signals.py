"""Django signal handlers for the videos app."""

import os
import shutil

import django_rq
from django.db.models.signals import post_delete, post_save
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


@receiver(post_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
    """
    Delete all media files from disk when a video is deleted.

    Removes the original video file, the thumbnail and the entire
    HLS directory containing all converted segments.

    Args:
        sender: The model class sending the signal (Video).
        instance (Video): The deleted Video instance.
        **kwargs: Additional signal keyword arguments.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
    hls_dir = os.path.normpath(os.path.join(
        os.path.dirname(instance.video_file.path),
        '..', str(instance.pk)
    ))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)