"""Views for video listing and HLS streaming."""

import os

from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer
from .utils import (
    get_manifest_path,
    get_segment_path,
    is_valid_resolution,
    is_video_ready,
)


class VideoListView(APIView):
    """Return a list of all available videos with metadata."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return all videos ordered newest first.

        Args:
            request: The authenticated HTTP request.

        Returns:
            Response: 200 with a list of video metadata objects.
        """
        videos = Video.objects.all()
        serializer = VideoSerializer(
            videos, many=True, context={'request': request}
        )
        return Response(serializer.data)


class HLSManifestView(APIView):
    """Serve the HLS .m3u8 playlist for a given video and resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """
        Return the HLS manifest file for the given video and resolution.

        Args:
            request: The authenticated HTTP request.
            movie_id (int): Primary key of the video.
            resolution (str): Desired resolution, e.g. '720p'.

        Returns:
            FileResponse: The .m3u8 file with HLS content type.

        Raises:
            Http404: If resolution is invalid, video not ready,
                     or manifest file does not exist on disk.
        """
        if not is_valid_resolution(resolution) or not is_video_ready(movie_id):
            raise Http404
        manifest_path = get_manifest_path(movie_id, resolution)
        if not os.path.exists(manifest_path):
            raise Http404
        return FileResponse(
            open(manifest_path, 'rb'),
            content_type='application/vnd.apple.mpegurl',
        )


class HLSSegmentView(APIView):
    """Serve a single HLS .ts video segment."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """
        Return a binary HLS video segment file.

        Args:
            request: The authenticated HTTP request.
            movie_id (int): Primary key of the video.
            resolution (str): Desired resolution, e.g. '720p'.
            segment (str): Segment filename, e.g. '000.ts'.

        Returns:
            FileResponse: The .ts segment with binary content type.

        Raises:
            Http404: If resolution is invalid, video not ready,
                     or segment file does not exist on disk.
        """
        if not is_valid_resolution(resolution) or not is_video_ready(movie_id):
            raise Http404
        segment_path = get_segment_path(movie_id, resolution, segment)
        if not os.path.exists(segment_path):
            raise Http404
        return FileResponse(
            open(segment_path, 'rb'),
            content_type='video/MP2T',
        )
