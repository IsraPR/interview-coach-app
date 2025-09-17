from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path(
        "ws/interview/live-interaction/",
        consumers.SpeechToSpeechConsumer.as_asgi(),
    ),
]
