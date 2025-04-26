# myproject/asgi.py
import os, django, traceback, sys
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import Notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.production')
django.setup()

# crea primero la app real
django_asgi_app = get_asgi_application()
application_inner = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(Notifications.routing.websocket_urlpatterns)
        )
    ),
})

# ahora define un wrapper ASGI correcto
async def exception_logging_middleware(scope, receive, send):
    try:
        await application_inner(scope, receive, send)
    except Exception:
        # fuerza que la traza salga por stderr para que Render la capture
        traceback.print_exc(file=sys.stderr)
        raise

# finalmente, asignas el wrapper como tu aplicación ASGI
application = exception_logging_middleware
