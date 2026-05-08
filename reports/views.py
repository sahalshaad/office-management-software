from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from reports.services import export_attendance_csv, export_attendance_pdf, export_attendance_xlsx, productivity_snapshot


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productivity"] = productivity_snapshot(None if self.request.user.is_admin_role else self.request.user)
        return context


class AttendanceCSVExportView(LoginRequiredMixin, View):
    def get(self, request):
        return export_attendance_csv(request)


class AttendanceXLSXExportView(LoginRequiredMixin, View):
    def get(self, request):
        return export_attendance_xlsx(request)


class AttendancePDFExportView(LoginRequiredMixin, View):
    def get(self, request):
        return export_attendance_pdf(request)
