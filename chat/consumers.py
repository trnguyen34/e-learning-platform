import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # scope contains information about its connection, 
        # arugments passed by the URL, and authenticated user.  
        self.user = self.scope['user']
        # retrieve the course id from scope. 
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'
        
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # accept the WebSocket connection
        await self.accept()
        
    async def disconnect(self, close_code):
        
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # receive messages from WebSocket
    async def receive(self, text_data):
        # json.loads() parse the valid text_data JSON and
        # convert it into dict.
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                # 'type' is a special key that corresponds 
                # to the name of the method that will be 
                # invoked on comsumers that receive the event.
                # In this case, chat_message() method will be 
                # call.
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )
        
    # receive message from room group
    async def chat_message(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))