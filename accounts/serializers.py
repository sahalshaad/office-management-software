from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import Department

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "description", "manager", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "employee_id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "department",
            "department_name",
            "designation",
            "address",
            "joining_date",
            "profile_photo",
            "emergency_contact",
            "role",
            "status",
            "email_verified",
        ]
        read_only_fields = ["email_verified"]


class StaffCreateUpdateSerializer(UserSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=10)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["password"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "employee_id", "email", "first_name", "last_name", "full_name", "phone", "address", "profile_photo", "emergency_contact", "department_name", "designation", "role", "status"]
        read_only_fields = ["username", "employee_id", "email", "department_name", "designation", "role", "status"]
