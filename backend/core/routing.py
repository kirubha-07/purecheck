from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    re_path(r'ws/alerts/(?P<city>\w+)/$', consumers.AlertConsumer.as_asgi()),
]
