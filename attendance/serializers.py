from rest_framework import serializers

from attendance.models import Attendance, AttendanceAttempt, OfficeLocation


class OfficeLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeLocation
        fields = ["id", "name", "address", "latitude", "longitude", "radius_meters", "start_time", "end_time", "late_grace_minutes", "is_active"]


class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    office_name = serializers.CharField(source="office.name", read_only=True)
    working_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "user",
            "user_name",
            "employee_id",
            "office",
            "office_name",
            "date",
            "punch_in_at",
            "punch_out_at",
            "punch_in_latitude",
            "punch_in_longitude",
            "punch_out_latitude",
            "punch_out_longitude",
            "punch_in_distance_m",
            "punch_out_distance_m",
            "gps_accuracy_m",
            "punch_in_ip",
            "punch_out_ip",
            "status",
            "work_seconds",
            "working_hours",
            "is_manual",
            "correction_reason",
            "notes",
            "selfie",
        ]
        read_only_fields = [
            "punch_in_ip",
            "punch_out_ip",
            "punch_in_device",
            "punch_out_device",
            "work_seconds",
            "selfie",
        ]


class PunchSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    accuracy_m = serializers.DecimalField(max_digits=9, decimal_places=2, required=False, allow_null=True)
    selfie_data = serializers.CharField(required=False, allow_blank=True, write_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class AttendanceAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceAttempt
        fields = ["id", "user", "action", "allowed", "reason", "latitude", "longitude", "accuracy_m", "distance_m", "ip_address", "user_agent", "created_at"]
