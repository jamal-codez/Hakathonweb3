from django.urls import path
from . import views

urlpatterns = [
    path("login/",views.LoginApiView.as_view()),
    path("register/",views.RegisterUserAPIView.as_view()),
    path("my-groups/",views.GetAllUserSolariGroupApiView.as_view()),#
    path("solarigroup/<slug:id>/messages/",views.GetSolariGroupMessagesApiView.as_view()),#
    path("chats/", views.UserChatSpaceView.as_view()), 
    path("chats/start/", views.StartUserChatView.as_view()), 
    path("chats/messages/", views.GetUserChatMessagesView.as_view()),
]