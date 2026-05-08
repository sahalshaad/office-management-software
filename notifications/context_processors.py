from notifications.services import notification_queryset_for


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {"unread_notifications_count": 0, "latest_notifications": []}
    qs = notification_queryset_for(request.user).exclude(read_by=request.user)
    return {"unread_notifications_count": qs.count(), "latest_notifications": qs[:5]}
