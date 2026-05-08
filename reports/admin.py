from django.contrib import admin

from reports.models import PerformanceLog


@admin.register(PerformanceLog)
class PerformanceLogAdmin(admin.ModelAdmin):
    list_display = ("user", "period_start", "period_end", "attendance_percentage", "task_completion_rate", "productivity_score")
    list_filter = ("period_start", "period_end")
    search_fields = ("user__email", "user__employee_id")
