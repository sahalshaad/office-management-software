from django.contrib import admin

from attendance.models import Attendance, AttendanceAttempt, OfficeLocation


@admin.register(OfficeLocation)
class OfficeLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "radius_meters", "start_time", "late_grace_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "address")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "status", "punch_in_at", "punch_out_at", "working_hours", "is_manual", "is_deleted")
    list_filter = ("status", "date", "office", "is_manual", "is_deleted")
    search_fields = ("user__first_name", "user__last_name", "user__employee_id", "user__email")
    readonly_fields = ("work_seconds", "created_at", "updated_at")
    date_hierarchy = "date"

    def get_queryset(self, request):
        return Attendance.all_objects.all()


@admin.register(AttendanceAttempt)
class AttendanceAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "allowed", "distance_m", "ip_address", "created_at")
    list_filter = ("action", "allowed", "created_at")
    search_fields = ("user__email", "user__employee_id", "ip_address", "reason")
    readonly_fields = ("created_at", "updated_at")
