"""Admin configuration for the videos app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin panel for Video management.

    Shows thumbnail previews, HLS status badges, category filters,
    and bulk actions to reset processing status for debugging.
    """

    list_display = [
        'title',
        'category',
        'hls_status_badge',
        'thumbnail_preview',
        'created_at',
    ]
    list_filter = ['category', 'hls_ready', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['hls_ready', 'created_at', 'thumbnail_preview_large']
    ordering = ['-created_at']
    actions = ['mark_hls_ready', 'mark_hls_not_ready']

    fieldsets = (
        ('Video Details', {
            'fields': ('title', 'description', 'category')
        }),
        ('Media Files', {
            'fields': (
                'video_file', 'thumbnail', 'thumbnail_preview_large'
            )
        }),
        ('Processing Status', {
            'fields': ('hls_ready', 'created_at')
        }),
    )

    @admin.display(description='HLS Status')
    def hls_status_badge(self, obj):
        """Render a coloured badge showing the HLS conversion status."""
        if obj.hls_ready:
            return mark_safe(
                '<span style="color:green;font-weight:bold;">'
                '✔ Ready</span>'
            )
        return mark_safe(
            '<span style="color:orange;font-weight:bold;">'
            '⏳ Processing</span>'
        )

    @admin.display(description='Thumbnail')
    def thumbnail_preview(self, obj):
        """Render a small thumbnail image in the list view."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />',
                obj.thumbnail.url,
            )
        return '–'

    @admin.display(description='Preview')
    def thumbnail_preview_large(self, obj):
        """Render a larger thumbnail preview in the video detail view."""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height:200px;'
                'border-radius:6px;" />',
                obj.thumbnail.url,
            )
        return 'No thumbnail yet – will be generated after processing.'

    @admin.action(description='Mark selected videos as HLS ready')
    def mark_hls_ready(self, request, queryset):
        """Bulk-set hls_ready=True on selected videos."""
        updated = queryset.update(hls_ready=True)
        self.message_user(request, f'{updated} video(s) marked as ready.')

    @admin.action(description='Mark selected videos as not ready')
    def mark_hls_not_ready(self, request, queryset):
        """Bulk-set hls_ready=False on selected videos."""
        updated = queryset.update(hls_ready=False)
        self.message_user(
            request, f'{updated} video(s) marked as not ready.'
        )