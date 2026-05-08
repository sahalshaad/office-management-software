from django.urls import path

from leaves import views

app_name = "leaves"

urlpatterns = [
    path("", views.LeaveListView.as_view(), name="list"),
    path("apply/", views.LeaveCreateView.as_view(), name="apply"),
    path("<int:pk>/review/", views.LeaveReviewView.as_view(), name="review"),
]
