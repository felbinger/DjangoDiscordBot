"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

from os import environ
from asyncio import ensure_future

from django.core.asgi import get_asgi_application

environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
application = get_asgi_application()

from django.conf import settings  # noqa: E402

from .bot import bot  # noqa: E402

ensure_future(bot.start(settings.DISCORD_BOT_TOKEN))
