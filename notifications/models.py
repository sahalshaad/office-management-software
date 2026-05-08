from django.conf import settings
from django.db import models

from core.models import SoftDeleteModel


class Notification(SoftDeleteModel):
    class Type(models.TextChoices):
        ANNOUNCEMENT = "announcement", "Announcement"
        MEETING = "meeting", "Meeting Alert"
        EVENT = "event", "Event"
        EMERGENCY = "emergency", "Emergency"
        TASK = "task", "Task"
        ATTENDANCE = "attendance", "Attendance"
        LEAVE = "leave", "Leave"

    title = models.CharField(max_length=180)
    message = models.TextField()
    notification_type = models.CharField(max_length=24, choices=Type.choices, default=Type.ANNOUNCEMENT, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="notifications")
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="read_notifications")
    target_role = models.CharField(max_length=24, blank=True, db_index=True)
    is_global = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["notification_type", "created_at"]), models.Index(fields=["is_global", "target_role"])]

    def is_read_by(self, user):
        return self.read_by.filter(pk=user.pk).exists()

    def __str__(self):
        return self.title
