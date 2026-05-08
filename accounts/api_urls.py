from rest_framework.routers import DefaultRouter

from accounts.api import DepartmentViewSet, UserViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet)
router.register("staff", UserViewSet)

urlpatterns = router.urls
