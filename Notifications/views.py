from rest_framework import viewsets, permissions
from Notifications.models import Notification
from Notifications.serializer import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # cada usuario ve solo sus notificaciones
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # permitir que solo se marque como leído
        serializer.save()


