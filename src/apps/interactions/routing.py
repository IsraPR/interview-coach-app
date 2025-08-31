from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/interview/interaction/", consumers.SpeechToSpeechConsumer.as_asgi()
    ),
]
