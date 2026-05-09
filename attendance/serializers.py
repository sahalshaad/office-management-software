from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from rest_framework import serializers

from attendance.models import Attendance, AttendanceAttempt, OfficeLocation


class GPSDecimalField(serializers.DecimalField):
    """Custom DecimalField that normalizes GPS coordinates to 8 decimal places."""

    def to_internal_value(self, data):
        """Convert and normalize GPS coordinate to Decimal with 8 decimal places."""
        if data is None:
            return None
        try:
            if isinstance(data, float):
                data = str(data)
            decimal_value = Decimal(data)
            normalized = decimal_value.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
            return normalized
        except (InvalidOperation, ValueError, TypeError):
            self.fail('invalid')

    def validate_field_value(self, data):
        """Validate the normalized value."""
        return super().to_internal_value(data)


class AccuracyDecimalField(serializers.DecimalField):
    """Custom DecimalField that normalizes GPS accuracy to 2 decimal places."""

    def to_internal_value(self, data):
        """Convert and normalize GPS accuracy to Decimal with 2 decimal places."""
        if data is None:
            return None
        try:
            if isinstance(data, float):
                data = str(data)
            decimal_value = Decimal(data)
            normalized = decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return normalized
        except (InvalidOperation, ValueError, TypeError):
            self.fail('invalid')

    def validate_field_value(self, data):
        return super().to_internal_value(data)


class OfficeLocationSerializer(serializers.ModelSerializer):
    latitude = GPSDecimalField(max_digits=12, decimal_places=8)
    longitude = GPSDecimalField(max_digits=12, decimal_places=8)

    class Meta:
        model = OfficeLocation
        fields = ["id", "name", "address", "latitude", "longitude", "radius_meters", "start_time", "end_time", "late_grace_minutes", "is_active"]

    def validate_latitude(self, value):
        """Validate latitude is within valid range."""
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        """Validate longitude is within valid range."""
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


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
    latitude = GPSDecimalField(max_digits=12, decimal_places=8)
    longitude = GPSDecimalField(max_digits=12, decimal_places=8)
    accuracy_m = AccuracyDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    selfie_data = serializers.CharField(required=False, allow_blank=True, write_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_latitude(self, value):
        """Validate latitude is within valid range."""
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        """Validate longitude is within valid range."""
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_accuracy_m(self, value):
        """Validate GPS accuracy is non-negative and normalized."""
        if value is None:
            return None
        if value < 0:
            raise serializers.ValidationError("Accuracy must be zero or positive.")
        return value


class AttendanceAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceAttempt
        fields = ["id", "user", "action", "allowed", "reason", "latitude", "longitude", "accuracy_m", "distance_m", "ip_address", "user_agent", "created_at"]
