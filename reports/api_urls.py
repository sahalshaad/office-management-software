from rest_framework.routers import DefaultRouter

from reports.api import PerformanceLogViewSet, ReportSummaryViewSet

router = DefaultRouter()
router.register("performance", PerformanceLogViewSet)
router.register("summary", ReportSummaryViewSet, basename="report-summary")

urlpatterns = router.urls
