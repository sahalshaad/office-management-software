from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import Department, User


class OfficeFlowAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or username", widget=forms.TextInput(attrs={"autofocus": True}))


class StaffForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text="Leave blank to keep the current password.")

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "employee_id",
            "email",
            "phone",
            "department",
            "designation",
            "address",
            "joining_date",
            "profile_photo",
            "emergency_contact",
            "role",
            "status",
        ]
        widgets = {"joining_date": forms.DateInput(attrs={"type": "date"})}

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "address", "profile_photo", "emergency_contact"]


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code", "description", "manager"]
