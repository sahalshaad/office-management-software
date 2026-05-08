from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class PerformanceLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="performance_logs")
    period_start = models.DateField()
    period_end = models.DateField()
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    working_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    task_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    leave_days = models.PositiveIntegerField(default=0)
    productivity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ai_summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-period_end"]
        unique_together = ("user", "period_start", "period_end")
        indexes = [models.Index(fields=["user", "period_start", "period_end"]), models.Index(fields=["productivity_score"])]

    def __str__(self):
        return f"{self.user} performance {self.period_start} to {self.period_end}"
