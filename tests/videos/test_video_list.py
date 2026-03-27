"""Tests for the video list endpoint."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from tests.base import VideoflixTestCase, UserFactory
from videos.models import Video


class VideoListViewTest(VideoflixTestCase):
    """Test suite for GET /api/video/."""

    def setUp(self):
        """Set up the URL and authenticate a test user."""
        super().setUp()
        self.url = reverse('video-list')
        self.user = UserFactory()
        self.authenticate(self.user)

    def _create_video(self, title='Test Movie', category='drama'):
        """
        Create and return a Video instance for use in tests.

        Args:
            title (str): The video title.
            category (str): The video category.

        Returns:
            Video: The created Video instance.
        """
        return Video.objects.create(
            title=title,
            description='A test video.',
            category=category,
            video_file=SimpleUploadedFile(
                'test.mp4', b'video content', content_type='video/mp4'
            ),
            hls_ready=True,
        )

    def test_video_list_returns_200_for_authenticated_user(self):
        """An authenticated request should return HTTP 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_list_returns_401_for_unauthenticated_user(self):
        """A request without authentication must return HTTP 401."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_video_list_returns_all_videos(self):
        """The endpoint should return all videos in the database."""
        self._create_video('Movie A')
        self._create_video('Movie B')
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_video_list_contains_required_fields(self):
        """Each video object must include all required metadata fields."""
        self._create_video()
        response = self.client.get(self.url)
        video_data = response.data[0]
        required_fields = [
            'id', 'title', 'description',
            'category', 'thumbnail_url', 'created_at',
        ]
        for field in required_fields:
            self.assertIn(field, video_data)

    def test_video_list_ordered_newest_first(self):
        """Videos must be returned in descending creation order."""
        self._create_video('Old Movie')
        self._create_video('New Movie')
        response = self.client.get(self.url)
        self.assertEqual(response.data[0]['title'], 'New Movie')

    def test_empty_database_returns_empty_list(self):
        """The endpoint must return an empty list if no videos exist."""
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])
