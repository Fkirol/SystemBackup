from rest_framework.routers import DefaultRouter
from Notifications.views import NotificationViewSet
from django.urls import path,include


router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
#router.register(r'trigger', trigger_ws_test, basename='trigger')

urlpatterns = [
    path("", include(router.urls)),    
]

