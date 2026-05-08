import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="PerformanceLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("attendance_percentage", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("working_hours", models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ("task_completion_rate", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("leave_days", models.PositiveIntegerField(default=0)),
                ("productivity_score", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("ai_summary", models.TextField(blank=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="performance_logs", to=django.conf.settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-period_end"],
                "unique_together": {("user", "period_start", "period_end")},
                "indexes": [
                    models.Index(fields=["user", "period_start", "period_end"], name="reports_per_user_id_d6c688_idx"),
                    models.Index(fields=["productivity_score"], name="reports_per_product_b1c923_idx"),
                ],
            },
        ),
    ]
