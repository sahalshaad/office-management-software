from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.OfficeFlowLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    path("verify-email/<uidb64>/<token>/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path("staff/new/", views.StaffCreateView.as_view(), name="staff_create"),
    path("staff/<int:pk>/edit/", views.StaffUpdateView.as_view(), name="staff_update"),
    path("staff/<int:pk>/delete/", views.StaffDeleteView.as_view(), name="staff_delete"),
    path("departments/", views.DepartmentListView.as_view(), name="departments"),
    path("departments/new/", views.DepartmentCreateView.as_view(), name="department_create"),
]
