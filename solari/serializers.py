
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.conf import settings

from .models import *
# from .validators import password_validator

class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ['token','is_active','is_staff','is_superuser','date_joined','last_login']
        extra_kwargs = {'password': {'write_only': True},'pin': {'write_only': True},
                        'groups':{'write_only': True},'user_permissions':{'write_only':True}}
    def validate(self,value):
        try:
            django_validate_password(value['password'])
        except ValidationError as err:
            raise serializers.ValidationError({'password':err})
        return value
    
    def get_token(self,obj):
        """
        returns the token of the user if it exists and if it does not exist, it creates a token and returns it
        """
        return Token.objects.get_or_create(user = obj)[0].key
    

class SolariGroupSerializer(serializers.ModelSerializer):
    chat_id = serializers.SerializerMethodField()
    class Meta:
        model = SolariGroup
        fields = ["id","admin","name","chat_id","description","picture","date_created"]
        read_only_fields = ["admin"]
    
    def create(self, validated_data):
        obj = super().create(validated_data)
        SolariGroupChatSpace.objects.create(group = obj)
        return obj
    def get_chat_id(self,obj):
        chat = SolariGroupChatSpace.objects.get(group = obj)
        return str(chat.id)
        


class UserChatSpaceSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    class Meta:
        model = UserChatSpace
        fields =["id","chat_name"]
    def get_chat_name(self,obj):
        user = self.context['request'].user
        chat = obj.users.exclude(id = user.id)
        chat_name = chat.first().full_name
        return chat_name

class SolariGroupChatSpaceSerializer(serializers.ModelSerializer):
    chat_name = serializers.SerializerMethodField()
    class Meta:
        model = SolariGroupChatSpace
        fields =["id","chat_name"]
    def get_chat_name(self,obj):
        return obj.group.name

class UserMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    # audio_duration = serializers.SerializerMethodField()
    class Meta:
        model = UserMessage
        fields = ['id','type','sender','sender_name','content','file','created','filename']

    def get_sender_name(self,obj):
        return obj.sender.full_name
    def get_filename(self,obj):
        if obj.file:
            return obj.file.name.rsplit("/",maxsplit = 2)[-1]
        else:
            return None

class SolariGroupMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    # filename = serializers.SerializerMethodField()
    # audio_duration = serializers.SerializerMethodField()
    class Meta:
        model = SolariGroupMessage
        fields = ['id','type','sender','sender_name','content','file','created']

    def get_sender_name(self,obj):
        return obj.sender.full_name
    # def get_filename(self,obj):
    #     if obj.file:
    #         return obj.file.name.rsplit("/",maxsplit = 2)[-1]
    #     else:
    #         return None