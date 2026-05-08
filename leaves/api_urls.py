from rest_framework.routers import DefaultRouter

from leaves.api import LeaveBalanceViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("requests", LeaveRequestViewSet)
router.register("balances", LeaveBalanceViewSet)

urlpatterns = router.urls
