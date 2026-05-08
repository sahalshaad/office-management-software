from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import SoftDeleteModel, TimeStampedModel


class Department(SoftDeleteModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=24, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["code", "name"])]

    def __str__(self):
        return self.name


class User(AbstractUser, SoftDeleteModel):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        HR_ADMIN = "hr_admin", "HR/Admin"
        STAFF = "staff", "Staff Employee"

    class EmploymentStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.STAFF, db_index=True)
    phone = models.CharField(max_length=32, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")
    designation = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    emergency_contact = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE, db_index=True)
    email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ["first_name", "last_name", "employee_id"]
        indexes = [
            models.Index(fields=["role", "status"]),
            models.Index(fields=["department", "status"]),
            models.Index(fields=["employee_id"]),
        ]

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        return self.role in {self.Role.SUPER_ADMIN, self.Role.HR_ADMIN}

    def __str__(self):
        return f"{self.full_name} ({self.employee_id or self.username})"


class UserLoginAudit(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_audits", null=True, blank=True)
    email_or_username = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    successful = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["ip_address", "created_at"]), models.Index(fields=["successful"])]

    def __str__(self):
        return f"{self.email_or_username} - {'ok' if self.successful else 'failed'}"
