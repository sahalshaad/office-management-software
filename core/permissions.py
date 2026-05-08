from rest_framework.permissions import BasePermission


ADMIN_ROLES = {"super_admin", "hr_admin"}


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ADMIN_ROLES)


class IsOwnerOrAdminRole(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ADMIN_ROLES:
            return True
        owner = getattr(obj, "user", None) or getattr(obj, "employee", None) or getattr(obj, "assigned_to", None)
        return owner == request.user
