from discord import Intents
from discord.ext.commands import Bot
from importlib import import_module
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

bot = Bot(
    command_prefix=settings.DISCORD_BOT_PREFIX,
    case_insensitive=True,
    description=settings.DISCORD_BOT_DESCRIPTION,
    intents=Intents.all(),
)

for app in settings.INSTALLED_APPS:
    app_name, *_ = app.split(".apps")

    # skip modules without cogs
    try:
        loaded_cog = import_module(f'{app_name}.cogs')
    except ModuleNotFoundError:
        continue

    if '__all__' not in dir(loaded_cog):
        logger.warning(f"Unable to load cog {app_name}: __app__ not found!")
        continue

    # TODO possible security vulnerability: find solution without eval() / exec()!
    for cog in loaded_cog.__all__:
        exec(f'from {app_name}.cogs import {cog}')
        bot.add_cog(eval(cog)(bot))
