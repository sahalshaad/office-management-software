from django.urls import path

from attendance import views

app_name = "attendance"

urlpatterns = [
    path("", views.AttendancePageView.as_view(), name="punch"),
    path("history/", views.AttendanceHistoryView.as_view(), name="history"),
    path("office-settings/", views.OfficeSettingsView.as_view(), name="office_settings"),
]
