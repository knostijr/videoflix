"""Admin configuration for the users app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin panel configuration for CustomUser.

    Provides search, filters, bulk activation actions
    and a coloured active/inactive status badge.
    """

    model = CustomUser
    list_display = [
        'email',
        'is_active_badge',
        'is_staff',
        'created_at',
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        ('Account', {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            )
        }),
        ('Metadata', {'fields': ('created_at', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'is_active', 'is_staff',
            ),
        }),
    )

    @admin.display(description='Active')
    def is_active_badge(self, obj):
        """Render a coloured badge for the user's active status."""
        if obj.is_active:
            return mark_safe(
                '<span style="color:green;font-weight:bold;">'
                'Active</span>'
            )
        return mark_safe(
            '<span style="color:red;font-weight:bold;">'
            'Inactive</span>'
        )

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        """Bulk-activate all selected user accounts."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f'{updated} user(s) successfully activated.'
        )

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        """Bulk-deactivate all selected user accounts."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f'{updated} user(s) successfully deactivated.'
        )
