from rest_framework import serializers

from leaves.models import LeaveBalance, LeaveRequest
from leaves.services import review_leave_request


class LeaveRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True)
    days = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "user",
            "user_name",
            "leave_type",
            "start_date",
            "end_date",
            "days",
            "reason",
            "document",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "admin_remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "status", "reviewed_by", "reviewed_at", "admin_remarks", "created_at", "updated_at"]

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError("End date must be after start date.")
        return attrs


class LeaveBalanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = LeaveBalance
        fields = ["id", "user", "user_name", "casual_balance", "sick_balance", "paid_balance", "emergency_balance", "updated_at"]


class LeaveReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[LeaveRequest.Status.APPROVED, LeaveRequest.Status.REJECTED])
    admin_remarks = serializers.CharField(required=False, allow_blank=True)

    def save(self, leave, reviewer):
        return review_leave_request(leave, reviewer, self.validated_data["status"], self.validated_data.get("admin_remarks", ""))
