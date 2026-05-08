from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from core.permissions import ADMIN_ROLES


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ADMIN_ROLES

    def handle_no_permission(self):
        raise PermissionDenied


class EmployeeOrAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated
