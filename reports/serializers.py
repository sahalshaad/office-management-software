from rest_framework import serializers

from reports.models import PerformanceLog


class PerformanceLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = PerformanceLog
        fields = ["id", "user", "user_name", "period_start", "period_end", "attendance_percentage", "working_hours", "task_completion_rate", "leave_days", "productivity_score", "ai_summary"]
