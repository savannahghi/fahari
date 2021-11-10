"""
ASGI config for Fahari Reporting project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""
import os
import sys
from pathlib import Path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import re_path  # type: ignore
from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# fahari directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "fahari"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_asgi_app = get_asgi_application()

from fahari.misc.consumers import StockVerificationReceiptsAdapterConsumer  # noqa

application = ProtocolTypeRouter(
    {
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi_app,
        # WebSocket router
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(
                        r"^ws/misc/stock_receipts_verification_ingest/$",
                        StockVerificationReceiptsAdapterConsumer.as_asgi(),
                    ),
                ]
            )
        ),
    }
)
