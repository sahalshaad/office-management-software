from django import forms

from notifications.models import Notification


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["title", "message", "notification_type", "recipients", "target_role", "is_global"]
        widgets = {"recipients": forms.CheckboxSelectMultiple}
