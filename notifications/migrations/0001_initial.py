import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(max_length=180)),
                ("message", models.TextField()),
                ("notification_type", models.CharField(choices=[("announcement", "Announcement"), ("meeting", "Meeting Alert"), ("event", "Event"), ("emergency", "Emergency"), ("task", "Task"), ("attendance", "Attendance"), ("leave", "Leave")], db_index=True, default="announcement", max_length=24)),
                ("target_role", models.CharField(blank=True, db_index=True, max_length=24)),
                ("is_global", models.BooleanField(db_index=True, default=False)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sent_notifications", to=django.conf.settings.AUTH_USER_MODEL)),
                ("read_by", models.ManyToManyField(blank=True, related_name="read_notifications", to=django.conf.settings.AUTH_USER_MODEL)),
                ("recipients", models.ManyToManyField(blank=True, related_name="notifications", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["notification_type", "created_at"], name="notificatio_notific_b107a5_idx"),
                    models.Index(fields=["is_global", "target_role"], name="notificatio_is_glob_ccbcf5_idx"),
                ],
            },
        ),
    ]
