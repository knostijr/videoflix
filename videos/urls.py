"""URL configuration for the videos app."""

from django.urls import path

from . import views

urlpatterns = [
    path('video/', views.VideoListView.as_view(), name='video-list'),
    path(
        'video/<int:movie_id>/<str:resolution>/index.m3u8',
        views.HLSManifestView.as_view(),
        name='hls-manifest',
    ),
    path(
        'video/<int:movie_id>/<str:resolution>/<str:segment>/',
        views.HLSSegmentView.as_view(),
        name='hls-segment',
    ),
]
