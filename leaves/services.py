from django.utils import timezone

from leaves.models import LeaveBalance, LeaveRequest


def review_leave_request(leave, reviewer, status, remarks=""):
    previous_status = leave.status
    leave.status = status
    leave.admin_remarks = remarks
    leave.reviewed_by = reviewer
    leave.reviewed_at = timezone.now()
    leave.save(update_fields=["status", "admin_remarks", "reviewed_by", "reviewed_at", "updated_at"])
    if status == LeaveRequest.Status.APPROVED and previous_status != LeaveRequest.Status.APPROVED:
        balance, _ = LeaveBalance.objects.get_or_create(user=leave.user)
        field = f"{leave.leave_type}_balance"
        current = getattr(balance, field, 0)
        setattr(balance, field, max(current - leave.days, 0))
        balance.save(update_fields=[field, "updated_at"])
    return leave
