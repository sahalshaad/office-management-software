from rest_framework.routers import DefaultRouter

from tasks.api import TaskViewSet

router = DefaultRouter()
router.register("items", TaskViewSet)

urlpatterns = router.urls
