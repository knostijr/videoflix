"""Utility functions for HLS file path resolution and validation."""

import os

from django.conf import settings

from .models import Video


def get_hls_base_dir(movie_id, resolution):
    """
    Return the base directory path for HLS files of a video.

    Args:
        movie_id (int): The video's primary key.
        resolution (str): Resolution label, e.g. '720p'.

    Returns:
        str: Absolute path to the HLS directory.
    """
    return os.path.join(
        settings.MEDIA_ROOT, 'videos', str(movie_id), resolution
    )


def get_manifest_path(movie_id, resolution):
    """
    Return the absolute path to the .m3u8 playlist file.

    Args:
        movie_id (int): The video's primary key.
        resolution (str): The resolution label, e.g. '720p'.

    Returns:
        str: Absolute path to index.m3u8.
    """
    return os.path.join(
        get_hls_base_dir(movie_id, resolution), 'index.m3u8'
    )


def get_segment_path(movie_id, resolution, segment):
    """
    Return the absolute path to a specific HLS segment file.

    Args:
        movie_id (int): The video's primary key.
        resolution (str): The resolution label, e.g. '720p'.
        segment (str): Segment filename, e.g. '000.ts'.

    Returns:
        str: Absolute path to the .ts segment file.
    """
    return os.path.join(
        get_hls_base_dir(movie_id, resolution), segment
    )


def is_valid_resolution(resolution):
    """
    Check whether the requested resolution is supported.

    Args:
        resolution (str): The resolution string to validate.

    Returns:
        bool: True if the resolution is 480p, 720p or 1080p.
    """
    return resolution in ('480p', '720p', '1080p')


def is_video_ready(movie_id):
    """
    Check whether a video exists and its HLS conversion is complete.

    Args:
        movie_id (int): Primary key of the video.

    Returns:
        bool: True if the video exists and hls_ready is True.
    """
    return Video.objects.filter(pk=movie_id, hls_ready=True).exists()