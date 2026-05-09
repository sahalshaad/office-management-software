from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
import logging

from attendance.models import Attendance, AttendanceAttempt, OfficeLocation
from attendance.serializers import AttendanceAttemptSerializer, AttendanceSerializer, OfficeLocationSerializer, PunchSerializer
from attendance.services import AttendanceValidationError, attendance_dashboard_stats, punch_in, punch_out
from core.permissions import IsAdminRole

logger = logging.getLogger(__name__)


class OfficeLocationViewSet(ModelViewSet):
    queryset = OfficeLocation.objects.all()
    serializer_class = OfficeLocationSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["name", "address"]
    ordering_fields = ["name", "created_at"]


class AttendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.select_related("user", "office").all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["date", "status", "user", "office"]
    search_fields = ["user__first_name", "user__last_name", "user__employee_id", "user__email"]
    ordering_fields = ["date", "punch_in_at", "status"]

    def get_queryset(self):
        qs = self.queryset
        if not self.request.user.is_admin_role:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "correct"}:
            return [IsAdminRole()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="punch-in")
    def punch_in(self, request):
        serializer = PunchSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response({"detail": "Invalid request data: " + str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            attendance = punch_in(request.user, request, **serializer.validated_data)
        except AttendanceValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            # Catch any unexpected exceptions and return proper JSON error response
            logger.exception("Unexpected error in punch_in endpoint")
            return Response({"detail": "An unexpected error occurred. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(AttendanceSerializer(attendance, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="punch-out")
    def punch_out(self, request):
        serializer = PunchSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            return Response({"detail": "Invalid request data: " + str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            attendance = punch_out(request.user, request, **serializer.validated_data)
        except AttendanceValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            # Catch any unexpected exceptions and return proper JSON error response
            logger.exception("Unexpected error in punch_out endpoint")
            return Response({"detail": "An unexpected error occurred. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(AttendanceSerializer(attendance, context={"request": request}).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminRole])
    def correct(self, request, pk=None):
        attendance = self.get_object()
        serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        corrected = serializer.save(is_manual=True)
        corrected.refresh_work_seconds()
        corrected.save(update_fields=["work_seconds", "is_manual", "updated_at"])
        return Response(AttendanceSerializer(corrected, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        return Response(attendance_dashboard_stats(None if request.user.is_admin_role else request.user))


class AttendanceAttemptViewSet(ReadOnlyModelViewSet):
    queryset = AttendanceAttempt.objects.select_related("user", "office").all()
    serializer_class = AttendanceAttemptSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["action", "allowed", "user"]
    ordering_fields = ["created_at", "allowed"]
