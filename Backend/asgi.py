import os
import django
from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import Notifications.routing  # tu routing de WS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.production')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                Notifications.routing.websocket_urlpatterns
            )
        )
    ),
})
