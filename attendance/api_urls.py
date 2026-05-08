from rest_framework.routers import DefaultRouter

from attendance.api import AttendanceAttemptViewSet, AttendanceViewSet, OfficeLocationViewSet

router = DefaultRouter()
router.register("offices", OfficeLocationViewSet)
router.register("records", AttendanceViewSet)
router.register("attempts", AttendanceAttemptViewSet)

urlpatterns = router.urls
