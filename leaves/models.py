from django.conf import settings
from django.db import models

from core.models import SoftDeleteModel, TimeStampedModel


class LeaveRequest(SoftDeleteModel):
    class LeaveType(models.TextChoices):
        CASUAL = "casual", "Casual Leave"
        SICK = "sick", "Sick Leave"
        EMERGENCY = "emergency", "Emergency Leave"
        PAID = "paid", "Paid Leave"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=24, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    document = models.FileField(upload_to="leaves/documents/", null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_leaves")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status"]), models.Index(fields=["start_date", "end_date"])]

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user} - {self.leave_type} - {self.status}"


class LeaveBalance(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_balance")
    casual_balance = models.PositiveSmallIntegerField(default=12)
    sick_balance = models.PositiveSmallIntegerField(default=8)
    paid_balance = models.PositiveSmallIntegerField(default=15)
    emergency_balance = models.PositiveSmallIntegerField(default=5)

    def balance_for(self, leave_type):
        return getattr(self, f"{leave_type}_balance", 0)

    def __str__(self):
        return f"{self.user} leave balance"
