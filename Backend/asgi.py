import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(Notifications.routing.websocket_urlpatterns)
    ),
})
