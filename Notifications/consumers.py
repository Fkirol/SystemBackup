import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"notifications_{user.username}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WS CONNECTED: usuario={user.username}, grupo={self.group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WS DISCONNECTED: grupo={self.group_name}")

    async def notify(self, event):
        logger.info(f"WS SEND to {self.group_name}: {event['message']}")
        await self.send(text_data=json.dumps(event['message']))
        
