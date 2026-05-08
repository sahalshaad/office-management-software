from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminRole
from leaves.models import LeaveBalance, LeaveRequest
from leaves.serializers import LeaveBalanceSerializer, LeaveRequestSerializer, LeaveReviewSerializer
from notifications.models import Notification
from notifications.services import send_notification


class LeaveRequestViewSet(ModelViewSet):
    queryset = LeaveRequest.objects.select_related("user", "reviewed_by")
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "leave_type", "user"]
    search_fields = ["user__first_name", "user__last_name", "user__employee_id", "reason"]
    ordering_fields = ["start_date", "created_at", "status"]

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsAdminRole()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], permission_classes=[IsAdminRole])
    def review(self, request, pk=None):
        leave = self.get_object()
        serializer = LeaveReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        leave = serializer.save(leave, request.user)
        send_notification(
            "Leave request reviewed",
            f"Your {leave.get_leave_type_display()} request was {leave.get_status_display().lower()}.",
            Notification.Type.LEAVE,
            created_by=request.user,
            recipients=[leave.user],
        )
        return Response(LeaveRequestSerializer(leave, context={"request": request}).data)


class LeaveBalanceViewSet(ModelViewSet):
    queryset = LeaveBalance.objects.select_related("user")
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user"]

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminRole()]
        return super().get_permissions()
