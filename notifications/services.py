from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from accounts.models import User
from notifications.models import Notification


def notification_queryset_for(user):
    return (
        Notification.objects.filter(is_global=True)
        | Notification.objects.filter(target_role=user.role)
        | Notification.objects.filter(recipients=user)
    ).distinct()


def send_notification(title, message, notification_type=Notification.Type.ANNOUNCEMENT, created_by=None, recipients=None, target_role="", is_global=False):
    notification = Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        created_by=created_by,
        target_role=target_role,
        is_global=is_global,
    )
    if recipients:
        notification.recipients.set(recipients)
    users = User.objects.filter(is_active=True, status=User.EmploymentStatus.ACTIVE)
    if recipients:
        users = User.objects.filter(pk__in=[user.pk for user in recipients])
    elif target_role:
        users = users.filter(role=target_role)
    channel_layer = get_channel_layer()
    if channel_layer:
        payload = {
            "type": "notification.event",
            "id": notification.pk,
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "created_at": notification.created_at.isoformat(),
        }
        for user in users:
            async_to_sync(channel_layer.group_send)(f"user_{user.pk}", payload)
    return notification
