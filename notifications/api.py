from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminRole
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from notifications.services import notification_queryset_for, send_notification


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.prefetch_related("recipients", "read_by").select_related("created_by")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["notification_type", "is_global", "target_role"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "notification_type"]

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return self.queryset
        return notification_queryset_for(self.request.user)

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminRole()]
        return super().get_permissions()

    def perform_create(self, serializer):
        recipients = list(serializer.validated_data.pop("recipients", []))
        notification = send_notification(
            serializer.validated_data["title"],
            serializer.validated_data["message"],
            serializer.validated_data.get("notification_type", Notification.Type.ANNOUNCEMENT),
            created_by=self.request.user,
            recipients=recipients,
            target_role=serializer.validated_data.get("target_role", ""),
            is_global=serializer.validated_data.get("is_global", False),
        )
        serializer.instance = notification

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read_by.add(request.user)
        return Response({"ok": True})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        for notification in self.get_queryset().exclude(read_by=request.user):
            notification.read_by.add(request.user)
        return Response({"ok": True})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().exclude(read_by=request.user).count()
        return Response({"count": count})
