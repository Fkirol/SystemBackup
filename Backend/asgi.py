# myproject/asgi.py
import os, django, traceback, sys
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import Notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(Notifications.routing.websocket_urlpatterns)
        )
    ),
})

# Wrap to catch cualquier excepción
def exception_logging_middleware(scope, receive, send):
    try:
        return application(scope, receive, send)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise

application = exception_logging_middleware
