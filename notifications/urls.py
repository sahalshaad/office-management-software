from django.urls import path

from notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("new/", views.NotificationCreateView.as_view(), name="create"),
]
