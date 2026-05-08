import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("auth", "0012_alter_user_first_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("code", models.CharField(max_length=24, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("employee_id", models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ("role", models.CharField(choices=[("super_admin", "Super Admin"), ("hr_admin", "HR/Admin"), ("staff", "Staff Employee")], db_index=True, default="staff", max_length=24)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("designation", models.CharField(blank=True, max_length=120)),
                ("address", models.TextField(blank=True)),
                ("joining_date", models.DateField(blank=True, null=True)),
                ("profile_photo", models.ImageField(blank=True, null=True, upload_to="profiles/")),
                ("emergency_contact", models.CharField(blank=True, max_length=120)),
                ("status", models.CharField(choices=[("active", "Active"), ("inactive", "Inactive")], db_index=True, default="active", max_length=16)),
                ("email_verified", models.BooleanField(default=False)),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="employees", to="accounts.department")),
                ("groups", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.permission")),
            ],
            options={
                "ordering": ["first_name", "last_name", "employee_id"],
                "indexes": [
                    models.Index(fields=["role", "status"], name="accounts_us_role_71cf4b_idx"),
                    models.Index(fields=["department", "status"], name="accounts_us_depart_2dac47_idx"),
                    models.Index(fields=["employee_id"], name="accounts_us_employe_93be6d_idx"),
                ],
            },
        ),
        migrations.AddField(
            model_name="department",
            name="manager",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="managed_departments", to="accounts.user"),
        ),
        migrations.CreateModel(
            name="UserLoginAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email_or_username", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("successful", models.BooleanField(default=False)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="login_audits", to="accounts.user")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["ip_address", "created_at"], name="accounts_us_ip_addr_594d4e_idx"),
                    models.Index(fields=["successful"], name="accounts_us_success_b95474_idx"),
                ],
            },
        ),
        migrations.AddIndex(model_name="department", index=models.Index(fields=["code", "name"], name="accounts_de_code_17ac2e_idx")),
    ]
