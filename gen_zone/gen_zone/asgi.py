import os
import django
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from chat.middlewares import WebSocketJWTAuthMiddleware

from channels.routing import ProtocolTypeRouter, URLRouter
from chat import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gen_zone.settings')
django.setup()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(URLRouter(routing.websocket_urlpatterns)),
    }
)
