from django.shortcuts import render


import logging
from django.core.files import File
from io import BytesIO
import base64
from operator import attrgetter
from decimal import Decimal
# import requests
from rest_framework.parsers import MultiPartParser, FormParser

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import HttpRequest
from django.conf import settings
import datetime
# from .utils import NotificationGenerator, NotificationSender, NotificationType
from django.http import Http404
# import magic


from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# # from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

# from .models import *
from .serializers import *

# Create your views here.
class RegisterUserAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        if User.objects.filter(email = request.data['email']).exists():
            return Response({'message':"User email already exists"},status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = self.perform_create(serializer, request)
        headers = self.get_success_headers(serializer.data)

        return Response({'message':'created'}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, request):
        password = serializer.validated_data['password']
        obj = serializer.save()
        instance = User.objects.get(id = obj.id)
        instance.set_password(password)
        instance.save()
        return self.create_user_token(instance)
    def create_user_token(self,user):
        token = Token.objects.create(user = user)
        return token


class LoginApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args,**kwargs):
        if "email" not in request.data or "password" not in request.data:
            raise AuthenticationFailed({"message":"Email and password must be provided"})

        email = request.data['email']
        password = request.data['password']
        user = authenticate(request,email = email,password = password)
        if not user:
            return Response({'message':"Incorrect Credentials"},status.HTTP_401_UNAUTHORIZED)
        data = UserSerializer(
                user
            ).data
        user.last_login=timezone.now()
        user.save()
        # login_history = LoginHistory(user=user)
        # login_history.save()
        
        return Response(data)


class CreateSolariGroupApiView(APIView):
    def post(self,request):
        data = request.data
        serializer = SolariGroupSerializer(data = data)
        serializer.is_valid(raise_exception=True)
        serializer.save(admin = request.user)
        return Response(serializer.data)
    

class GetAllUserSolariGroupApiView(ListAPIView):
    serializer_class = SolariGroupSerializer
    def get_queryset(self):
        user = self.request.user
        groups = user.solari_groups.all()
        admin_groups = user.solarigroup_set.all()
        combined_groups = admin_groups | groups
        return combined_groups.distinct()
    

class GetSolariGroupMessagesApiView(APIView):
    def get(self,request,id):
        try:
            group = SolariGroup.objects.get(id = id)
        except SolariGroup.DoesNotExist:
            return Response({"message":"Unknown group"}, status=status.HTTP_404_NOT_FOUND)
        messages = SolariGroupMessage.objects.filter(chatspace = group.solarigroupchatspace).order_by("-created").select_related('chatspace')
        serializer = SolariGroupMessageSerializer(messages,many = True)
        return Response(serializer.data)
    
# class SendGroupMessagesApiView(APIView):
#     def get(self,request,id):
#         try:
#             group = SolariGroup.objects.get(id = id)
#         except SolariGroup.DoesNotExist:
#             return Response({"message":"Unknown group"}, status=status.HTTP_404_NOT_FOUND)
#         self.check_object_permissions(request,group)
#         messages = SolariGroupMessage.objects.filter(chatspace = group.groupchatspace).order_by("-created").select_related('chatspace')
#         serializer = SolariGroupMessageSerializer(messages,many = True)
#         return Response(serializer.data)

class UserChatSpaceView(ListAPIView):
    serializer_class = UserChatSpaceSerializer
    def get_queryset(self):
        user = self.request.user
        chatspace = UserChatSpace.objects.filter(users = user) 
        return chatspace

class GetUserChatMessagesView(ListAPIView):
    serializer_class = UserMessageSerializer
    def get(self, request, *args, **kwargs):
        if not "chat" in request.query_params:
            return Response({'message':"no chat specified"},status=400)
        chatspace = UserChatSpace.objects.filter(id = request.query_params['chat'])
        if not chatspace.exists():
            return Response({'message':"invalid chat"},status=400)
        chatspace = chatspace.first()
        if request.user not in chatspace.users.all():
            return Response({'message':'cannot view messages'}, status=403)
        self.chatspace = chatspace
        return super().get(request, *args, **kwargs)
    def get_queryset(self):
        return UserMessage.objects.filter(chatspace = self.chatspace)

class StartUserChatView(APIView):
    def post(self,request):
        if not 'user' in request.data:
            return Response({'message':'user not specified'}, status=400)
        user_id = request.data['user']
        user_to_chat = User.objects.get(id = user_id)
        user = request.user
        chatspace = UserChatSpace.objects.filter(users = user_to_chat).filter(users = user)
        if chatspace.exists():
            chatspace = chatspace.first()
        else:
            chatspace = UserChatSpace()
            chatspace.save()
            chatspace.users.add(user, user_to_chat)
        
        serialized_data = UserChatSpaceSerializer(chatspace, context={"request":request})
        chat = chatspace.users.exclude(id = user.id)
        chat_name = chat.first().full_name
        return Response({**serialized_data.data,"chat_name":chat_name})
        
class SendUserMessagesApiView(APIView):
    def get(self,request,id):
        try:
            group = SolariGroup.objects.get(id = id)
        except SolariGroup.DoesNotExist:
            return Response({"message":"Unknown"}, status=status.HTTP_404_NOT_FOUND)
        messages = SolariGroupMessage.objects.filter(chatspace = group.solarigroupchatspace).order_by("-created").select_related('chatspace')
        serializer = SolariGroupMessageSerializer(messages,many = True)
        return Response(serializer.data)