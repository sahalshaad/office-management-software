from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminRole
from notifications.models import Notification
from notifications.services import send_notification
from tasks.models import Task, TaskAttachment, TaskComment
from tasks.serializers import TaskAttachmentSerializer, TaskCommentSerializer, TaskProgressSerializer, TaskSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.select_related("assigned_to", "created_by").prefetch_related("comments", "attachments")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "priority", "assigned_to", "created_by"]
    search_fields = ["title", "description", "assigned_to__first_name", "assigned_to__last_name", "assigned_to__employee_id"]
    ordering_fields = ["due_date", "priority", "status", "created_at"]

    def get_queryset(self):
        qs = self.queryset
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(Q(assigned_to=self.request.user) | Q(created_by=self.request.user))

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"} and not self.request.user.is_admin_role:
            return TaskProgressSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        send_notification(
            "New task assigned",
            task.title,
            Notification.Type.TASK,
            created_by=self.request.user,
            recipients=[task.assigned_to],
        )

    def get_permissions(self):
        if self.action in {"destroy"}:
            return [IsAdminRole()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="comments")
    def add_comment(self, request, pk=None):
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(task=task, author=request.user)
        return Response(TaskCommentSerializer(comment, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="attachments")
    def add_attachment(self, request, pk=None):
        task = self.get_object()
        serializer = TaskAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save(task=task, uploaded_by=request.user)
        return Response(TaskAttachmentSerializer(attachment, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="progress")
    def update_progress(self, request, pk=None):
        task = self.get_object()
        try:
            progress = int(request.data.get("progress", task.progress))
        except (TypeError, ValueError):
            return Response({"detail": "Progress must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        status_value = request.data.get("status")
        task.progress = max(0, min(progress, 100))
        if status_value:
            task.status = status_value
        elif task.progress > 0 and task.status == Task.Status.PENDING:
            task.status = Task.Status.IN_PROGRESS
        task.save()
        return Response(TaskSerializer(task, context={"request": request}).data)
