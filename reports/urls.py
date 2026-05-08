from django.urls import path

from reports import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsView.as_view(), name="index"),
    path("attendance.csv", views.AttendanceCSVExportView.as_view(), name="attendance_csv"),
    path("attendance.xlsx", views.AttendanceXLSXExportView.as_view(), name="attendance_xlsx"),
    path("attendance.pdf", views.AttendancePDFExportView.as_view(), name="attendance_pdf"),
]
