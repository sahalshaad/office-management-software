from django.urls import path

from notifications.consumers import OfficeFlowConsumer

websocket_urlpatterns = [path("ws/officeflow/", OfficeFlowConsumer.as_asgi())]
