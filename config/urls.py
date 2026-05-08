from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import DashboardView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("attendance/", include("attendance.urls")),
    path("tasks/", include("tasks.urls")),
    path("leaves/", include("leaves.urls")),
    path("notifications/", include("notifications.urls")),
    path("reports/", include("reports.urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("accounts.api_urls")),
    path("api/attendance/", include("attendance.api_urls")),
    path("api/tasks/", include("tasks.api_urls")),
    path("api/leaves/", include("leaves.api_urls")),
    path("api/notifications/", include("notifications.api_urls")),
    path("api/reports/", include("reports.api_urls")),
    path(
        "manifest.webmanifest",
        TemplateView.as_view(template_name="pwa/manifest.webmanifest", content_type="application/manifest+json"),
        name="manifest",
    ),
    path(
        "service-worker.js",
        TemplateView.as_view(template_name="pwa/service-worker.js", content_type="application/javascript"),
        name="service_worker",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
