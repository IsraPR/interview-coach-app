from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/interview/", consumers.SpeechToSpeechConsumer.as_asgi()),
]
