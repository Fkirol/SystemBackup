import json
import logging
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            return await self.close()

        self.group_name = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WS CONNECTED: usuario={user.username}, grupo={self.group_name}")

        pending = await self.get_unread_notifications(user)
        ids = [notif.id for notif in pending]
        logger.info(f"Tengo {len(pending)} notificaciones pendientes: {ids}")
        for notif in pending:
            await self.send_json({
                "id": notif.id,
                "status": notif.status,
                "message": notif.message,
                "created_at": notif.created_at.isoformat(),
                "historical": True,
            })
            
        if ids:
            await self.mark_as_read(ids)
            logger.info(f"Marcadas como leídas: {ids}")

    @database_sync_to_async
    def get_unread_notifications(self, user):
        from Notifications.models import Notification
        qs = Notification.objects.filter(user=user.id, read=False)
        return list(qs)
    
    @database_sync_to_async
    def mark_as_read(self, ids):
        from Notifications.models import Notification
        Notification.objects.filter(id__in=ids).update(read=True)
        
    def mark_as_rea(self, notification_id: int):
        from Notifications.models import Notification
        Notification.objects.filter(id=notification_id).update(read=True)
        
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"WS DISCONNECTED: grupo={self.group_name}")

    async def notify(self, event):
        message = event['message']
        await self.send_json(message)
        await self.mark_as_rea(message['id'])
        
