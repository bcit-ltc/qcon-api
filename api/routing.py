# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws', consumers.TextConsumer.as_asgi()),
    # re_path(r'ws/(?P<session_id>\w+)/$', consumers.TextConsumer.as_asgi()),
]