from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import SoftDeleteModel, TimeStampedModel


class Task(SoftDeleteModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=180)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_tasks")
    priority = models.CharField(max_length=16, choices=Priority.choices, default=Priority.MEDIUM, db_index=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING, db_index=True)
    due_date = models.DateTimeField(db_index=True)
    progress = models.PositiveSmallIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["priority", "status"]),
        ]

    @property
    def is_overdue(self):
        return self.status not in {self.Status.COMPLETED, self.Status.REJECTED} and self.due_date < timezone.now()

    def save(self, *args, **kwargs):
        if self.progress >= 100 and self.status != self.Status.REJECTED:
            self.status = self.Status.COMPLETED
            self.completed_at = self.completed_at or timezone.now()
        elif self.is_overdue and self.status == self.Status.PENDING:
            self.status = self.Status.OVERDUE
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TaskAttachment(TimeStampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="tasks/attachments/")
    label = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.label or self.file.name


class TaskComment(TimeStampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_comments")
    comment = models.TextField()
    attachment = models.FileField(upload_to="tasks/comments/", null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author}: {self.comment[:40]}"
