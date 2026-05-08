from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from leaves.forms import LeaveRequestForm, LeaveReviewForm
from leaves.models import LeaveBalance, LeaveRequest
from leaves.services import review_leave_request
from notifications.models import Notification
from notifications.services import send_notification


class LeaveListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = "leaves/leave_list.html"
    context_object_name = "leaves"
    paginate_by = 20

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related("user", "reviewed_by")
        if not self.request.user.is_admin_role:
            qs = qs.filter(user=self.request.user)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["balance"] = LeaveBalance.objects.filter(user=self.request.user).first()
        return context


class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = "leaves/leave_form.html"
    success_url = reverse_lazy("leaves:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Leave request submitted.")
        return super().form_valid(form)


class LeaveReviewView(LoginRequiredMixin, UpdateView):
    model = LeaveRequest
    form_class = LeaveReviewForm
    template_name = "leaves/leave_review.html"
    success_url = reverse_lazy("leaves:list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin_role:
            return redirect("leaves:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        review_leave_request(self.object, self.request.user, form.cleaned_data["status"], form.cleaned_data.get("admin_remarks", ""))
        messages.success(self.request, "Leave request reviewed.")
        send_notification(
            "Leave request reviewed",
            f"Your {self.object.get_leave_type_display()} request was {self.object.get_status_display().lower()}.",
            Notification.Type.LEAVE,
            created_by=self.request.user,
            recipients=[self.object.user],
        )
        return redirect(self.get_success_url())
