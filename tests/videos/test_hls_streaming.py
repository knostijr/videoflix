"""Tests for the HLS manifest and segment streaming endpoints."""

import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from tests.base import VideoflixTestCase, UserFactory
from videos.models import Video


class HLSManifestViewTest(VideoflixTestCase):
    """Test suite for GET /api/video/<id>/<resolution>/index.m3u8."""

    def setUp(self):
        """Set up a video and create a fake manifest file on disk."""
        super().setUp()
        self.user = UserFactory()
        self.authenticate(self.user)
        self.video = Video.objects.create(
            title='Stream Test',
            video_file=SimpleUploadedFile(
                'test.mp4', b'mp4data', content_type='video/mp4'
            ),
            hls_ready=True,
        )
        self._create_fake_manifest('720p')

    def _create_fake_manifest(self, resolution):
        """
        Write a minimal .m3u8 file to disk so the view can serve it.

        Args:
            resolution (str): The resolution folder to create, e.g. '720p'.
        """
        hls_dir = os.path.join(
            settings.MEDIA_ROOT,
            'videos', str(self.video.pk), resolution,
        )
        os.makedirs(hls_dir, exist_ok=True)
        with open(os.path.join(hls_dir, 'index.m3u8'), 'w') as f:
            f.write('#EXTM3U\n#EXT-X-VERSION:3\n')

    def test_manifest_returns_200_for_valid_request(self):
        """A valid manifest request should return HTTP 200."""
        url = reverse('hls-manifest', kwargs={
            'movie_id': self.video.pk,
            'resolution': '720p',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manifest_returns_correct_content_type(self):
        """The manifest content-type must be the HLS MIME type."""
        url = reverse('hls-manifest', kwargs={
            'movie_id': self.video.pk,
            'resolution': '720p',
        })
        response = self.client.get(url)
        self.assertIn(
            'application/vnd.apple.mpegurl',
            response.get('Content-Type', ''),
        )

    def test_manifest_returns_404_for_unsupported_resolution(self):
        """An unrecognised resolution string should return HTTP 404."""
        url = reverse('hls-manifest', kwargs={
            'movie_id': self.video.pk,
            'resolution': '8k',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manifest_returns_404_for_nonexistent_video(self):
        """A request for a non-existent video ID should return HTTP 404."""
        url = reverse('hls-manifest', kwargs={
            'movie_id': 99999,
            'resolution': '720p',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manifest_returns_401_without_authentication(self):
        """An unauthenticated streaming request must return HTTP 401."""
        self.client.logout()
        url = reverse('hls-manifest', kwargs={
            'movie_id': self.video.pk,
            'resolution': '720p',
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)