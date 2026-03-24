"""Views for video listing and HLS streaming."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer


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
        """Placeholder – implemented fully on Day 12."""
        return Response({'detail': 'Coming on Day 12.'}, status=501)


class HLSSegmentView(APIView):
    """Serve an individual HLS .ts segment file."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Placeholder – will be implemented if necessary"""
        return Response({'detail': 'Coming on Day 12.'}, status=501)