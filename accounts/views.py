from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import DepartmentForm, OfficeFlowAuthenticationForm, ProfileForm, StaffForm
from accounts.models import Department, User, UserLoginAudit
from accounts.services import send_verification_email
from accounts.tokens import email_verification_token
from core.mixins import AdminRequiredMixin


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class OfficeFlowLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = OfficeFlowAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        key = f"login-block:{client_ip(request)}"
        if cache.get(key, 0) >= 8:
            return HttpResponseForbidden("Too many login attempts. Try again in a few minutes.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        UserLoginAudit.objects.create(
            user=form.get_user(),
            email_or_username=form.cleaned_data.get("username", ""),
            ip_address=client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            successful=True,
        )
        cache.delete(f"login-block:{client_ip(self.request)}")
        login(self.request, form.get_user())
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        key = f"login-block:{client_ip(self.request)}"
        cache.set(key, cache.get(key, 0) + 1, timeout=600)
        UserLoginAudit.objects.create(
            email_or_username=self.request.POST.get("username", ""),
            ip_address=client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            successful=False,
        )
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)


class StaffListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/staff_list.html"
    context_object_name = "staff"
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.select_related("department").all()
        query = self.request.GET.get("q")
        department = self.request.GET.get("department")
        if query:
            qs = qs.filter(first_name__icontains=query) | qs.filter(last_name__icontains=query) | qs.filter(email__icontains=query) | qs.filter(employee_id__icontains=query)
        if department:
            qs = qs.filter(department_id=department)
        return qs.order_by("first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departments"] = Department.objects.all()
        return context


class StaffCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = StaffForm
    template_name = "accounts/staff_form.html"
    success_url = reverse_lazy("accounts:staff_list")

    def form_valid(self, form):
        messages.success(self.request, "Staff member created.")
        response = super().form_valid(form)
        send_verification_email(self.request, self.object)
        return response


class StaffUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = StaffForm
    template_name = "accounts/staff_form.html"
    success_url = reverse_lazy("accounts:staff_list")

    def form_valid(self, form):
        messages.success(self.request, "Staff member updated.")
        return super().form_valid(form)


class StaffDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "base/confirm_delete.html"
    success_url = reverse_lazy("accounts:staff_list")

    def form_valid(self, form):
        messages.success(self.request, "Staff member archived.")
        return super().form_valid(form)


class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = "accounts/department_list.html"
    context_object_name = "departments"


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "accounts/department_form.html"
    success_url = reverse_lazy("accounts:departments")


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError):
            return HttpResponseBadRequest("Invalid verification link.")
        if email_verification_token.check_token(user, token):
            user.email_verified = True
            user.save(update_fields=["email_verified", "updated_at"])
            messages.success(request, "Email verified.")
            return redirect("dashboard")
        return HttpResponseBadRequest("Invalid or expired verification link.")
