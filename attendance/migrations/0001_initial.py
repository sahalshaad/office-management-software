import datetime
import django.conf
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="OfficeLocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(default="Head Office", max_length=120)),
                ("address", models.TextField(blank=True)),
                ("latitude", models.DecimalField(decimal_places=7, max_digits=10)),
                ("longitude", models.DecimalField(decimal_places=7, max_digits=10)),
                ("radius_meters", models.PositiveIntegerField(default=50)),
                ("start_time", models.TimeField(default=datetime.time(9, 30))),
                ("end_time", models.TimeField(default=datetime.time(18, 30))),
                ("late_grace_minutes", models.PositiveIntegerField(default=10)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
            ],
            options={"ordering": ["name"], "indexes": [models.Index(fields=["is_active"], name="attendance__is_acti_519b7d_idx")]},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("date", models.DateField(db_index=True, default=django.utils.timezone.localdate)),
                ("punch_in_at", models.DateTimeField(blank=True, null=True)),
                ("punch_out_at", models.DateTimeField(blank=True, null=True)),
                ("punch_in_latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("punch_in_longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("punch_out_latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("punch_out_longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("punch_in_distance_m", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("punch_out_distance_m", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("gps_accuracy_m", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("punch_in_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("punch_out_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("punch_in_device", models.TextField(blank=True)),
                ("punch_out_device", models.TextField(blank=True)),
                ("selfie", models.ImageField(blank=True, null=True, upload_to="attendance/selfies/")),
                ("status", models.CharField(choices=[("present", "Present"), ("late", "Late"), ("absent", "Absent"), ("half_day", "Half Day"), ("on_leave", "On Leave")], db_index=True, default="present", max_length=24)),
                ("work_seconds", models.PositiveIntegerField(default=0)),
                ("is_manual", models.BooleanField(default=False)),
                ("correction_reason", models.TextField(blank=True)),
                ("notes", models.TextField(blank=True)),
                ("office", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="attendance_records", to="attendance.officelocation")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_records", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-date", "-punch_in_at"],
                "indexes": [
                    models.Index(fields=["date", "status"], name="attendance__date_6daf1a_idx"),
                    models.Index(fields=["user", "date"], name="attendance__user_id_7d98b8_idx"),
                    models.Index(fields=["punch_in_at"], name="attendance__punch_i_5fab25_idx"),
                ],
                "constraints": [models.UniqueConstraint(fields=("user", "date"), name="unique_attendance_per_user_date")],
            },
        ),
        migrations.CreateModel(
            name="AttendanceAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(choices=[("in", "Punch In"), ("out", "Punch Out")], max_length=16)),
                ("allowed", models.BooleanField(default=False)),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("accuracy_m", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("distance_m", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("office", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="attendance.officelocation")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendance_attempts", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "created_at"], name="attendance__user_id_514ed0_idx"),
                    models.Index(fields=["allowed", "action"], name="attendance__allowed_d218a1_idx"),
                ],
            },
        ),
    ]
