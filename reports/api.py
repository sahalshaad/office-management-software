from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from reports.models import PerformanceLog
from reports.serializers import PerformanceLogSerializer
from reports.services import productivity_snapshot


class PerformanceLogViewSet(ReadOnlyModelViewSet):
    queryset = PerformanceLog.objects.select_related("user")
    serializer_class = PerformanceLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "period_start", "period_end"]
    ordering_fields = ["period_end", "productivity_score"]

    def get_queryset(self):
        if self.request.user.is_admin_role:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class ReportSummaryViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="productivity")
    def productivity(self, request):
        snapshot = productivity_snapshot(None if request.user.is_admin_role else request.user)
        return Response(
            [
                {
                    "user": item["user"].full_name,
                    "employee_id": item["user"].employee_id,
                    "attendance_percentage": item["attendance_percentage"],
                    "working_hours": item["working_hours"],
                    "task_completion_rate": item["task_completion_rate"],
                    "leave_days": item["leave_days"],
                    "productivity_score": item["productivity_score"],
                    "insight": item["insight"],
                }
                for item in snapshot
            ]
        )
