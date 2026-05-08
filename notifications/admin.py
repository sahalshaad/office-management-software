from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "notification_type", "created_by", "target_role", "is_global", "created_at")
    list_filter = ("notification_type", "is_global", "target_role", "created_at")
    search_fields = ("title", "message")
    filter_horizontal = ("recipients", "read_by")
