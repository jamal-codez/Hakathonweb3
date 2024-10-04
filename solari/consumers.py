from io import BytesIO
import base64
import datetime
import time
import sys

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer

from django.core.files import File
from django.conf import settings

from .models import PersonalChatSpace, PersonalMessage, User, NotificationBox, MessageTypes, CommunityChatSpace, CommunityMessage
from .serializers import PersonalMessageSerializer, CommunityMessageSerializer
# import mimetypes
# import re

# CUSTOM_MIME_TYPE_MAP = {
#     'application/jpg': 'jpg',
#     'image/jpeg': 'jpeg',
#     'image/png': 'png',
#     'application/pdf': 'pdf',
#     # Add more mappings if necessary
# }
# def get_file_extension(base64_string):
#     # Regular expression to extract the MIME type
#     match = re.match(r"data:(.*?);base64,", base64_string)
#     if match:
#         mime_type = match.group(1)
#         # Get the file extension based on the MIME type
#         extension = mimetypes.guess_extension(mime_type)
#         if extension:
#             extension = extension.lstrip('.')
#         else:
#             # Use custom mapping as a fallback
#             extension = CUSTOM_MIME_TYPE_MAP.get(mime_type)
#         return extension
#     return None
class PersonalChatConsumer(AsyncJsonWebsocketConsumer):
    """
    The Websocket Connection Consumer for Personal Chats 
    """
    def user_in_chat(self,chat_id,user):
        chat = PersonalChatSpace.objects.get(id = chat_id)
        if user in chat.users.all():
            return True
        else:
            print(f"{self.user} has failed to {self.chat_name}")
            raise StopConsumer()
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["id"]
        # user = self.scope["user"]
        user_id= self.scope["url_route"]["kwargs"]["sender_id"]
        user=await database_sync_to_async(User.objects.get)(id = user_id)
        await database_sync_to_async(self.user_in_chat)(self.chat_id,user)
        self.user = user
        self.chat_name = f"chat_{self.chat_id}"
        await self.channel_layer.group_add(self.chat_name,self.channel_name)
        print(f"{self.user} has connected to {self.chat_name}")
        self.message_type = {MessageTypes.AUDIO:self.chat_audio,MessageTypes.TEXT:self.chat_text,MessageTypes.DOCUMENT:self.chat_document}
        await self.accept()

    async def disconnect(self, close_code):
        self.channel_layer.group_discard(
            self.chat_name, self.channel_name
        )
        self.close(close_code)
    async def receive_json(self, content, **kwargs):
        typ = content.get("type")
        if typ in self.message_type:
            await self.message_type[typ](content)
        else:
            self.send_json({
                "type": "error",
                "message":"invalid request format"
            })
    async def chat_text(self,event):
        chatspace = await database_sync_to_async(PersonalChatSpace.objects.get)(id = self.chat_id)
        message = PersonalMessage()
        message.type = MessageTypes.TEXT
        message.chatspace = chatspace
        message.content = event['content']
        # print(self.user)
        # user = await database_sync_to_async(User.objects.get)(id = int(event['sender']))
        # message.sender = user
        # message.sender = self.scope["user"]
        message.sender = self.user
        await database_sync_to_async(message.save)()
        send_data = PersonalMessageSerializer(message).data
        # print(send_data)
        await self.channel_layer.group_send(
            self.chat_name,
            {
            "type":"send_data",
            "data":{**send_data}
            })
    async def send_data(self,event):
        # print(event)
        await self.send_json(event['data'])
    async def chat_document(self,event):
        file_bytes = event['file']
        extension = event.get('extension')
        file = BytesIO(file_bytes)
        file.seek(0, 2)
        if sys.getsizeof(file) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            await self.send_json(
                {
                    "type": "error",
                    "message": "file is too large. file must be less than 25mb"
                }
            )
            return
        # print(file)
        try:
            
            chatspace = await database_sync_to_async(PersonalChatSpace.objects.get)(id = self.chat_id)
            message = PersonalMessage()
            message.type = MessageTypes.DOCUMENT
            message.chatspace = chatspace
            message.content = event.get("content")
            message.sender = self.user
            
            message.file = File(file=file,name=f'docs-{datetime.date.today()}-{time.time()}.{event.get("extension")}')
            await database_sync_to_async(message.save)()
            send_data = PersonalMessageSerializer(message).data
            await self.channel_layer.group_send(
            self.chat_name,
            {
            "type":"send_data",
            "data":{**send_data}
            })
        except Exception as e:
            print(e)
            await self.send_json(
            {
            "type":"error",
            "message":"failed to send"
            })
        finally:
            file.close()
    async def chat_audio(self,event):
        file_bytes = event['file']
        extension = event.get('extension')
        file = BytesIO(file_bytes)
        file.seek(0, 2)
        if sys.getsizeof(file) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            await self.send_json(
                {
                    "type": "error",
                    "message": "file is too large. file must be less than 25mb"
                }
            )
            return
        currentDate = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        
        try:
            
            chatspace = await database_sync_to_async(PersonalChatSpace.objects.get)(id = self.chat_id)
            message = PersonalMessage()
            message.type = MessageTypes.AUDIO
            message.chatspace = chatspace
            message.content = event.get("content")
            message.sender = self.user
            message.file = File(file,name=f"AUD-{currentDate}.mp3")
            await database_sync_to_async(message.save)()
            send_data = PersonalMessageSerializer(message).data
            await self.channel_layer.group_send(
                self.chat_name,
                {
                "type":"send_data",
                "data":{**send_data}
                })
        except Exception as err:
            print(err)
            await self.send_json({
                    "type": "error",
                    "message":"invalid audio file"
                })
        finally:
            file.close()

# class CommunityChatConsumer(AsyncJsonWebsocketConsumer):
#     """
#     The websocket connection consumer for the community chat
#     """
#     def user_in_community_chat(self,community_chat_id,user):
#         """
#         Validate user or vendor in community
#         """
#         community_chat = CommunityChatSpace.objects.get(id = community_chat_id)
#         if not user.is_authenticated:
            
#             print(f"{self.user} is not authenticated")
#             raise StopConsumer()
#         if user.is_vendor:
#             if user.vendor in community_chat.community.vendors.all():
#                 return True
#             else:
#                 print(f"{self.user} is vendor and not in coomunity")
#                 raise StopConsumer()
#         if user in community_chat.community.members.all():
#             return True
#         elif user == community_chat.community.admin:
#             return True
#         else:
#             print(f"{self.user} is not in community")
#             raise StopConsumer()
#     async def connect(self):
#         self.community_chat_id = self.scope["url_route"]["kwargs"]["id"]
#         # user = self.scope["user"]
#         user_id= self.scope["url_route"]["kwargs"]["user_id"]
#         user=await database_sync_to_async(User.objects.get)(id = user_id)
#         await database_sync_to_async(self.user_in_community_chat)(self.community_chat_id,user)
#         self.user = user
#         self.chat_name = f"community_{self.community_chat_id}"
#         await self.channel_layer.group_add(self.chat_name,self.channel_name)
#         print(f"{self.user} has connected to {self.chat_name}")
#         self.message_type = {MessageTypes.AUDIO:self.chat_audio,
#                              MessageTypes.TEXT:self.chat_text,
#                              MessageTypes.DOCUMENT:self.chat_document}
#         await self.accept()

#     async def disconnect(self, close_code):
#         self.channel_layer.group_discard(
#             self.chat_name, self.channel_name
#         )
#         self.close(close_code)
#     async def receive_json(self, content, **kwargs):
#         typ = content.get("type")
#         if typ in self.message_type:
#             await self.message_type[typ](content)
#         else:
#             self.send_json({
#                 "type": "error",
#                 "message":"invalid request format"
#             })
#     async def chat_text(self,event):
#         chatspace = await database_sync_to_async(CommunityChatSpace.objects.get)(id = self.community_chat_id)
#         message = CommunityMessage()
#         message.type = MessageTypes.TEXT
#         message.chatspace = chatspace
#         message.content = event['content']
#         # print(self.user)
#         # user = await database_sync_to_async(User.objects.get)(id = int(event['sender']))
#         # message.sender = user
#         # message.sender = self.scope["user"]
#         message.sender = self.user
#         await database_sync_to_async(message.save)()
#         send_data = CommunityMessageSerializer(message).data
#         # print(send_data)
#         await self.channel_layer.group_send(
#             self.chat_name,
#             {
#             "type":"send_data",
#             "data":{**send_data}
#             })
#     async def send_data(self,event):
#         # print(event)
#         await self.send_json(event['data'])

#     async def chat_document(self,event):
#         file_bytes = event['file']
#         extension = event.get('extension')
#         file = BytesIO(file_bytes)
#         file.seek(0, 2)
#         if sys.getsizeof(file) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
#             await self.send_json(
#                 {
#                     "type": "error",
#                     "message": "file is too large. file must be less than 25mb"
#                 }
#             )
#             return

#         try:
#             chatspace = await database_sync_to_async(CommunityChatSpace.objects.get)(id=self.community_chat_id)
#             message = CommunityMessage()
#             message.type = MessageTypes.DOCUMENT
#             message.chatspace = chatspace
#             message.content = event.get("content")
#             message.sender = self.user

#             message.file = File(file=file, name=f'docs-{datetime.date.today()}-{time.time()}.{extension}')
#             await database_sync_to_async(message.save)()
#             send_data = CommunityMessageSerializer(message).data
#             await self.channel_layer.group_send(
#                 self.chat_name,
#                 {
#                     "type": "send_data",
#                     "data": {**send_data}
#                 }
#             )
#         except Exception as e:
#             print(e)
#             await self.send_json(
#                 {
#                     "type": "error",
#                     "message": "failed to send"
#                 }
#             )
#         finally:
#             file.close()

#     async def chat_audio(self,event):
#         file_bytes = event['file']
#         extension = event.get('extension')
#         file = BytesIO(file_bytes)
#         file.seek(0, 2)
#         if sys.getsizeof(file) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
#             await self.send_json(
#                 {
#                     "type": "error",
#                     "message": "file is too large. file must be less than 25mb"
#                 }
#             )
#             return
#         currentDate = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        
#         try:
            
#             chatspace = await database_sync_to_async(CommunityChatSpace.objects.get)(id = self.community_chat_id)
#             message = CommunityMessage()
#             message.type = MessageTypes.AUDIO
#             message.chatspace = chatspace
#             message.content = event.get("content")
#             message.sender = self.user
#             message.file = File(file,name=f"AUD-{currentDate}.mp3")
#             await database_sync_to_async(message.save)()
#             send_data = CommunityMessageSerializer(message).data
#             await self.channel_layer.group_send(
#                 self.chat_name,
#                 {
#                 "type":"send_data",
#                 "data":{**send_data}
#                 })
#         except Exception as err:
#             print(err)
#             await self.send_json({
#                     "type": "error",
#                     "message":"invalid audio file"
#                 })
#         finally:
#             file.close()
            
class CommunityChatConsumer(AsyncJsonWebsocketConsumer):
    """
    The websocket connection consumer for the community chat
    """

    async def user_in_community_chat(self, community_chat_id, user):
        """
        Validate user or vendor in community
        """
        community_chat = await database_sync_to_async(CommunityChatSpace.objects.select_related('community').get)(id=community_chat_id)
        
        if not user.is_authenticated:
            print(f"{user} is not authenticated")
            raise StopConsumer()

        if user.is_vendor and user.vendor not in community_chat.community.vendors.all():
            print(f"{user} is vendor and not in community")
            raise StopConsumer()

        if user not in community_chat.community.members.all() and user != community_chat.community.admin:
            print(f"{user} is not in community")
            raise StopConsumer()

        return True

    async def connect(self):
        self.community_chat_id = self.scope["url_route"]["kwargs"]["id"]
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        user = await database_sync_to_async(User.objects.get)(id=user_id)

        await self.user_in_community_chat(self.community_chat_id, user)

        self.user = user
        self.chat_name = f"community_{self.community_chat_id}"

        await self.channel_layer.group_add(self.chat_name, self.channel_name)
        print(f"{self.user} has connected to {self.chat_name}")

        self.message_type = {
            MessageTypes.AUDIO: self.chat_audio,
            MessageTypes.TEXT: self.chat_text,
            MessageTypes.DOCUMENT: self.chat_document,
        }

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_name, self.channel_name)
        await self.close(close_code)

    async def receive_json(self, content, **kwargs):
        typ = content.get("type")
        if typ in self.message_type:
            await self.message_type[typ](content)
        else:
            await self.send_json({
                "type": "error",
                "message": "invalid request format"
            })

    async def chat_text(self, event):
        chatspace = await database_sync_to_async(CommunityChatSpace.objects.get)(id=self.community_chat_id)
        message = CommunityMessage(
            type=MessageTypes.TEXT,
            chatspace=chatspace,
            content=event['content'],
            sender=self.user
        )
        await database_sync_to_async(message.save)()
        send_data = CommunityMessageSerializer(message).data

        await self.channel_layer.group_send(
            self.chat_name,
            {
                "type": "send_data",
                "data": send_data
            }
        )

    async def send_data(self, event):
        await self.send_json(event['data'])

    async def chat_document(self, event):
        await self._handle_file(event, MessageTypes.DOCUMENT)

    async def chat_audio(self, event):
        await self._handle_file(event, MessageTypes.AUDIO)

    async def _handle_file(self, event, message_type):
        file_bytes = event['file']
        extension = event.get('extension')
        file = BytesIO(file_bytes)
        file.seek(0, 2)
        if sys.getsizeof(file) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            await self.send_json({
                "type": "error",
                "message": "file is too large. file must be less than 25mb"
            })
            return

        try:
            chatspace = await database_sync_to_async(CommunityChatSpace.objects.get)(id=self.community_chat_id)
            message = CommunityMessage(
                type=message_type,
                chatspace=chatspace,
                content=event.get("content"),
                sender=self.user,
                file=File(file, name=f'{message_type}-{datetime.date.today()}-{time.time()}.{extension}')
            )
            await database_sync_to_async(message.save)()
            send_data = CommunityMessageSerializer(message).data

            await self.channel_layer.group_send(
                self.chat_name,
                {
                    "type": "send_data",
                    "data": send_data
                }
            )
        except Exception as e:
            print(e)
            await self.send_json({
                "type": "error",
                "message": "failed to send"
            })
        finally:
            file.close()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    def user_has_notification_box(self,notification_id,user):
        notification = NotificationBox.objects.get(id = notification_id)
        if notification.user == user:
            return True
        else:
            raise StopConsumer()
    async def connect(self):
        self.notification_id = self.scope["url_route"]["kwargs"]["id"]
        user = self.scope["user"]
        # await database_sync_to_async(self.user_has_notification_box)(self.notification_id,user)
        self.user = user
        self.notification_name = f"notification_{self.notification_id}"
        await self.channel_layer.group_add(self.notification_name,self.channel_name)
        print(f"{user} is connected to notification {self.notification_id}" )
        await self.accept()
    async def send_notification(self,event):
        await self.send_json(event["data"])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.notification_name,self.channel_name)
        self.close(close_code)