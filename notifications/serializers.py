from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "created_by",
            "created_by_name",
            "recipients",
            "target_role",
            "is_global",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at", "is_read"]

    def get_is_read(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.read_by.filter(pk=request.user.pk).exists())
