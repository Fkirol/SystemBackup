from django.db import models
from django.conf import settings
from Databases.models import Backup

class Notification(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Successful'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.CharField(max_length=50,default=1)
    backup = models.ForeignKey(Backup,
                               on_delete=models.CASCADE,
                               related_name='notifications')
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES)   
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

