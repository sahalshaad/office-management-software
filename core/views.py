from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from attendance.services import attendance_dashboard_stats
from tasks.models import Task
from leaves.models import LeaveBalance, LeaveRequest
from core.permissions import ADMIN_ROLES


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_admin = user.role in ADMIN_ROLES
        context["is_admin_dashboard"] = is_admin
        context["attendance_stats"] = attendance_dashboard_stats(user=None if is_admin else user)
        tasks = Task.objects.select_related("assigned_to", "created_by")
        if not is_admin:
            tasks = tasks.filter(assigned_to=user)
        context["tasks_total"] = tasks.count()
        context["tasks_completed"] = tasks.filter(status=Task.Status.COMPLETED).count()
        context["tasks_overdue"] = sum(1 for task in tasks if task.is_overdue)
        context["recent_tasks"] = tasks.order_by("-created_at")[:6]
        if is_admin:
            context["pending_leaves"] = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()
        else:
            context["leave_balance"] = LeaveBalance.objects.filter(user=user).first()
            context["pending_leaves"] = LeaveRequest.objects.filter(user=user, status=LeaveRequest.Status.PENDING).count()
        return context
