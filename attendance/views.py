from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from attendance.models import Attendance, OfficeLocation
from core.mixins import AdminRequiredMixin


class AttendancePageView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/attendance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["office"] = OfficeLocation.objects.filter(is_active=True).first()
        context["today_record"] = Attendance.objects.filter(user=self.request.user).order_by("-date").first()
        return context


class AttendanceHistoryView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/history.html"
    context_object_name = "records"
    paginate_by = 25

    def get_queryset(self):
        qs = Attendance.objects.select_related("user", "office")
        if not self.request.user.is_admin_role:
            qs = qs.filter(user=self.request.user)
        staff = self.request.GET.get("staff")
        date = self.request.GET.get("date")
        if staff and self.request.user.is_admin_role:
            qs = qs.filter(user_id=staff)
        if date:
            qs = qs.filter(date=date)
        return qs.order_by("-date")


class OfficeSettingsView(AdminRequiredMixin, ListView):
    model = OfficeLocation
    template_name = "settings/office_locations.html"
    context_object_name = "offices"
