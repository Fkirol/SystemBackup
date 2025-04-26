from rest_framework import serializers
from Notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'status', 'message', 'created_at', 'read']
