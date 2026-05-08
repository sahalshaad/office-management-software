from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Department, User, UserLoginAudit


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "manager", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_deleted",)


@admin.register(User)
class OfficeFlowUserAdmin(UserAdmin):
    list_display = ("username", "employee_id", "email", "full_name", "role", "department", "status", "email_verified")
    list_filter = ("role", "status", "department", "email_verified", "is_deleted")
    search_fields = ("username", "email", "employee_id", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        (
            "OfficeFlow profile",
            {
                "fields": (
                    "employee_id",
                    "role",
                    "phone",
                    "department",
                    "designation",
                    "address",
                    "joining_date",
                    "profile_photo",
                    "emergency_contact",
                    "status",
                    "email_verified",
                    "is_deleted",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "OfficeFlow profile",
            {"fields": ("email", "employee_id", "role", "department", "status")},
        ),
    )


@admin.register(UserLoginAudit)
class UserLoginAuditAdmin(admin.ModelAdmin):
    list_display = ("email_or_username", "user", "ip_address", "successful", "created_at")
    list_filter = ("successful", "created_at")
    search_fields = ("email_or_username", "ip_address", "user__email")
    readonly_fields = ("created_at", "updated_at")
