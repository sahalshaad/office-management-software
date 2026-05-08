from django.contrib import admin

from leaves.models import LeaveBalance, LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "days", "status", "reviewed_by")
    list_filter = ("leave_type", "status", "start_date")
    search_fields = ("user__email", "user__employee_id", "reason")
    date_hierarchy = "start_date"


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "casual_balance", "sick_balance", "paid_balance", "emergency_balance")
    search_fields = ("user__email", "user__employee_id")
