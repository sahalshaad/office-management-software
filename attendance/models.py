from datetime import time

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.models import SoftDeleteModel, TimeStampedModel


class OfficeLocation(SoftDeleteModel):
    name = models.CharField(max_length=120, default="Head Office")
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    radius_meters = models.PositiveIntegerField(default=50)
    start_time = models.TimeField(default=time(9, 30))
    end_time = models.TimeField(default=time(18, 30))
    late_grace_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self):
        return f"{self.name} ({self.radius_meters}m)"


class Attendance(SoftDeleteModel):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        LATE = "late", "Late"
        ABSENT = "absent", "Absent"
        HALF_DAY = "half_day", "Half Day"
        ON_LEAVE = "on_leave", "On Leave"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    office = models.ForeignKey(OfficeLocation, on_delete=models.PROTECT, related_name="attendance_records")
    date = models.DateField(default=timezone.localdate, db_index=True)
    punch_in_at = models.DateTimeField(null=True, blank=True)
    punch_out_at = models.DateTimeField(null=True, blank=True)
    punch_in_latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    punch_in_longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    punch_out_latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    punch_out_longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    punch_in_distance_m = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    punch_out_distance_m = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    gps_accuracy_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    punch_in_ip = models.GenericIPAddressField(null=True, blank=True)
    punch_out_ip = models.GenericIPAddressField(null=True, blank=True)
    punch_in_device = models.TextField(blank=True)
    punch_out_device = models.TextField(blank=True)
    selfie = models.ImageField(upload_to="attendance/selfies/", null=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PRESENT, db_index=True)
    work_seconds = models.PositiveIntegerField(default=0)
    is_manual = models.BooleanField(default=False)
    correction_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date", "-punch_in_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                condition=Q(is_deleted=False),
                name="unique_attendance_per_user_date",
            )
        ]
        indexes = [
            models.Index(fields=["date", "status"]),
            models.Index(fields=["user", "date"]),
            models.Index(fields=["punch_in_at"]),
        ]

    @property
    def working_hours(self):
        return round(self.work_seconds / 3600, 2)

    def refresh_work_seconds(self):
        if self.punch_in_at and self.punch_out_at:
            self.work_seconds = max(int((self.punch_out_at - self.punch_in_at).total_seconds()), 0)
        return self.work_seconds

    def __str__(self):
        return f"{self.user} - {self.date} - {self.status}"


class AttendanceAttempt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_attempts")
    office = models.ForeignKey(OfficeLocation, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=16, choices=[("in", "Punch In"), ("out", "Punch Out")])
    allowed = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    accuracy_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance_m = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"]), models.Index(fields=["allowed", "action"])]

    def __str__(self):
        return f"{self.user} {self.action} {'allowed' if self.allowed else 'blocked'}"
