from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/personal-chat/<slug:id>/<slug:sender_id>/",consumers.PersonalChatConsumer.as_asgi()),
    path("ws/community-chat/<slug:id>/<slug:user_id>/",consumers.CommunityChatConsumer.as_asgi()),
    path("ws/notification/<slug:id>/",consumers.NotificationConsumer.as_asgi()),
]