import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="LeaveBalance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("casual_balance", models.PositiveSmallIntegerField(default=12)),
                ("sick_balance", models.PositiveSmallIntegerField(default=8)),
                ("paid_balance", models.PositiveSmallIntegerField(default=15)),
                ("emergency_balance", models.PositiveSmallIntegerField(default=5)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="leave_balance", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="LeaveRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("leave_type", models.CharField(choices=[("casual", "Casual Leave"), ("sick", "Sick Leave"), ("emergency", "Emergency Leave"), ("paid", "Paid Leave")], max_length=24)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField()),
                ("document", models.FileField(blank=True, null=True, upload_to="leaves/documents/")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")], db_index=True, default="pending", max_length=16)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("admin_remarks", models.TextField(blank=True)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_leaves", to=django.conf.settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="leave_requests", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["user", "status"], name="leaves_leav_user_id_cc28f0_idx"),
                    models.Index(fields=["start_date", "end_date"], name="leaves_leav_start_d_1e2fd0_idx"),
                ],
            },
        ),
    ]
