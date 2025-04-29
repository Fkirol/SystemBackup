from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

from Databases.models import Backup
from Notifications.models import Notification

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@receiver(post_save, sender=Backup)
def backup_status_notification(sender, instance, created, **kwargs):
    if created:
        return

    if instance.state == 2:
        status = Notification.STATUS_SUCCESS
        subject = 'Backup completado con exito'
        message = (
            
        )
    elif instance.state == 0:
        status = Notification.STATUS_FAILED
        subject = 'Backup FALLIDO'
        message = (
           
        )
    else:
        return
    try:
        notification = Notification.objects.create(
            user=instance.id_database.id_user,
            backup=instance,
            status=status,
            message=message,
        )
    except Exception as e:
        logger.error(f"Error al crear la notificación: {e}")
        return

    try:
        send_mail(
            subject="Se suscribio un pendejo",
            message="We're glad to have you on board!",
            from_email="codeslayersdevs@gmail.com",
            recipient_list=["lukushi040528@gmail.com"],
            fail_silently=False,
            )
    except Exception as e:
        logger.warning(f"Error enviando email de notificación: {e}")
    try:
        channel_layer = get_channel_layer()
        group_name = f"notifications_{instance.id_database.id_user}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notify',
                'message': {
                    'id': notification.id,
                    'status': notification.status,
                    'message': notification.message,
                    'created_at': notification.created_at.isoformat(),
                }
            }
        )
    except Exception as e:
        logger.warning(f"Error enviando notificación por WebSocket: {e}")
