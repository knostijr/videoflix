"""Background tasks for video processing with FFMPEG."""

import os
import subprocess

from django.conf import settings
from django.core.files import File

from .models import Video

RESOLUTIONS = {
    '480p':  {'width': 854,  'height': 480,  'bitrate': '800k'},
    '720p':  {'width': 1280, 'height': 720,  'bitrate': '2500k'},
    '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
}


def process_video_to_hls(video_id):
    """
    Convert an uploaded video to HLS format in all three resolutions.

    This is the main entry point called by the RQ worker.
    Orchestrates thumbnail generation and HLS conversion,
    then marks the video as ready for streaming.

    Args:
        video_id (int): Primary key of the Video instance to process.
    """
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return
    input_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
    generate_thumbnail(video_id)
    for resolution, config in RESOLUTIONS.items():
        output_dir = _build_output_dir(video_id, resolution)
        os.makedirs(output_dir, exist_ok=True)
        _convert_to_hls(input_path, output_dir, config)
    video.hls_ready = True
    video.save(update_fields=['hls_ready'])


def generate_thumbnail(video_id):
    """
    Extract a still frame at the 1-second mark and save it as thumbnail.

    Skips silently if the video already has a thumbnail assigned.

    Args:
        video_id (int): Primary key of the Video instance.
    """
    try:
        video = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        return
    if video.thumbnail:
        return
    input_path = os.path.join(settings.MEDIA_ROOT, str(video.video_file))
    thumbnail_path = _extract_frame(video_id, input_path)
    if thumbnail_path:
        _save_thumbnail(video, thumbnail_path)


def _build_output_dir(video_id, resolution):
    """
    Return the absolute path to the HLS output directory.

    Args:
        video_id (int): The video's primary key.
        resolution (str): Resolution label, e.g. '720p'.

    Returns:
        str: Absolute path to the output directory.
    """
    return os.path.join(
        settings.MEDIA_ROOT, 'videos', str(video_id), resolution
    )


def _convert_to_hls(input_path, output_dir, config):
    """
    Run FFMPEG to convert the video into HLS segments.

    Args:
        input_path (str): Absolute path to the source video file.
        output_dir (str): Directory to write .m3u8 and .ts files.
        config (dict): Resolution config with width, height, bitrate.
    """
    output_path = os.path.join(output_dir, 'index.m3u8')
    command = _build_ffmpeg_command(input_path, output_path, config)
    subprocess.run(command, check=True, capture_output=True)


def _build_ffmpeg_command(input_path, output_path, config):
    """
    Assemble the FFMPEG CLI command for HLS conversion.

    Args:
        input_path (str): Absolute path to the input video.
        output_path (str): Absolute path for the output .m3u8 file.
        config (dict): Dict with width, height and bitrate.

    Returns:
        list[str]: FFMPEG command as a list of argument strings.
    """
    segment_pattern = os.path.join(
        os.path.dirname(output_path), '%03d.ts'
    )
    return [
        'ffmpeg', '-i', input_path,
        '-vf', f"scale={config['width']}:{config['height']}",
        '-c:v', 'libx264',
        '-b:v', config['bitrate'],
        '-c:a', 'aac',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-hls_segment_filename', segment_pattern,
        '-f', 'hls',
        output_path, '-y',
    ]


def _extract_frame(video_id, input_path):
    """
    Use FFMPEG to extract one frame at the 1-second mark.

    Args:
        video_id (int): Used to create a unique thumbnail filename.
        input_path (str): Absolute path to the source video file.

    Returns:
        str | None: Path to the created thumbnail, or None on failure.
    """
    thumb_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails')
    os.makedirs(thumb_dir, exist_ok=True)
    output_path = os.path.join(thumb_dir, f'{video_id}_thumb.jpg')
    command = [
        'ffmpeg', '-i', input_path,
        '-ss', '00:00:01',
        '-vframes', '1',
        '-q:v', '2',
        output_path, '-y',
    ]
    result = subprocess.run(command, capture_output=True)
    return output_path if result.returncode == 0 else None


def _save_thumbnail(video, thumbnail_path):
    """
    Attach the extracted thumbnail file to the Video model.

    Args:
        video (Video): The Video instance to update.
        thumbnail_path (str): Absolute path to the thumbnail image file.
    """
    with open(thumbnail_path, 'rb') as f:
        filename = os.path.basename(thumbnail_path)
        video.thumbnail.save(filename, File(f), save=True)
