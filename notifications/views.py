import json

from accounts.models import Department, User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from core.mixins import AdminRequiredMixin
from notifications.forms import NotificationForm
from notifications.models import Notification
from notifications.services import notification_queryset_for, send_notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 25

    def get_queryset(self):
        return notification_queryset_for(self.request.user)


class NotificationCreateView(AdminRequiredMixin, CreateView):
    model = Notification
    form_class = NotificationForm
    template_name = "notifications/notification_form.html"
    success_url = reverse_lazy("notifications:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_queryset = (
            User.objects.filter(status=User.EmploymentStatus.ACTIVE)
            .select_related("department")
            .order_by("first_name", "last_name")
        )
        context["users"] = staff_queryset
        context["departments"] = Department.objects.all()
        context["role_choices"] = User.Role.choices
        context["users_json"] = json.dumps(
            [
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                    "role_label": user.get_role_display(),
                    "department": user.department.name if user.department else "Unassigned",
                    "initials": f"{(user.first_name[:1] or user.username[:1]).upper()}{(user.last_name[:1] or "").upper()}",
                }
                for user in staff_queryset
            ]
        )
        return context

    def form_valid(self, form):
        self.object = send_notification(
            form.cleaned_data["title"],
            form.cleaned_data["message"],
            form.cleaned_data["notification_type"],
            created_by=self.request.user,
            recipients=list(form.cleaned_data["recipients"]),
            target_role=form.cleaned_data["target_role"],
            is_global=form.cleaned_data["is_global"],
        )
        messages.success(self.request, "Notification sent.")
        return redirect(self.get_success_url())
