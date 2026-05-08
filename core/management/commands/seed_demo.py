from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Department, User
from attendance.models import Attendance, OfficeLocation
from leaves.models import LeaveBalance
from notifications.models import Notification
from tasks.models import Task


class Command(BaseCommand):
    help = "Create sample OfficeFlow data for local development."

    def handle(self, *args, **options):
        engineering, _ = Department.objects.get_or_create(code="ENG", defaults={"name": "Engineering"})
        operations, _ = Department.objects.get_or_create(code="OPS", defaults={"name": "Operations"})

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@officeflow.local",
                "first_name": "Aisha",
                "last_name": "Admin",
                "employee_id": "OF-0001",
                "role": User.Role.SUPER_ADMIN,
                "department": operations,
                "designation": "Operations Director",
                "is_staff": True,
                "is_superuser": True,
                "email_verified": True,
            },
        )
        admin.set_password("OfficeFlow123!")
        admin.save()

        staff, _ = User.objects.get_or_create(
            username="staff",
            defaults={
                "email": "staff@officeflow.local",
                "first_name": "Rahul",
                "last_name": "Sharma",
                "employee_id": "OF-0101",
                "role": User.Role.STAFF,
                "department": engineering,
                "designation": "Software Engineer",
                "email_verified": True,
            },
        )
        staff.set_password("OfficeFlow123!")
        staff.save()

        LeaveBalance.objects.get_or_create(user=staff)
        office, _ = OfficeLocation.objects.get_or_create(
            name="Bengaluru HQ",
            defaults={
                "address": "MG Road, Bengaluru",
                "latitude": 12.9715987,
                "longitude": 77.5945627,
                "radius_meters": 50,
                "is_active": True,
            },
        )

        now = timezone.now()
        Attendance.objects.get_or_create(
            user=staff,
            date=timezone.localdate(),
            defaults={
                "office": office,
                "punch_in_at": now - timedelta(hours=6),
                "punch_out_at": now - timedelta(hours=1),
                "punch_in_latitude": office.latitude,
                "punch_in_longitude": office.longitude,
                "punch_out_latitude": office.latitude,
                "punch_out_longitude": office.longitude,
                "punch_in_distance_m": 4,
                "punch_out_distance_m": 6,
                "status": Attendance.Status.PRESENT,
                "work_seconds": 18000,
            },
        )

        Task.objects.get_or_create(
            title="Prepare weekly operations report",
            defaults={
                "description": "Compile attendance, task progress, and leave highlights for this week.",
                "created_by": admin,
                "assigned_to": staff,
                "priority": Task.Priority.HIGH,
                "status": Task.Status.IN_PROGRESS,
                "due_date": now + timedelta(days=2),
                "progress": 45,
            },
        )

        Notification.objects.get_or_create(
            title="Welcome to OfficeFlow",
            defaults={
                "message": "Demo data is ready. Configure office coordinates before testing live geo attendance.",
                "notification_type": Notification.Type.ANNOUNCEMENT,
                "created_by": admin,
                "is_global": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data created. Admin/staff password: OfficeFlow123!"))
