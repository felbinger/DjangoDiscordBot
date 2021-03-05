from discord import Intents
from discord.ext.commands import Bot
from importlib import import_module
from django.conf import settings  # noqa: E402

bot = Bot(
    command_prefix=settings.DISCORD_BOT_PREFIX,
    case_insensitive=True,
    description=settings.DISCORD_BOT_DESCRIPTION,
    intents=(Intents.all()),
)

# TODO should be automatically configured using INSTALLED_APPS in settings.py
for app in settings.INSTALLED_APPS:
    app_name, *_ = app.split(".apps")

    # skip modules without cogs
    try:
        loaded_cog = import_module(f'{app_name}.cogs')
    except ModuleNotFoundError:
        continue

    if '__all__' not in dir(loaded_cog):
        print(f"Unable to load cog {app_name}: __app__ not found!")
        continue

    from user_manager.cogs import UserManager
    from log_manager.cogs import LogManager
    for cog in loaded_cog.__all__:
        print(f'from {app_name}.cogs import {cog}')
        # TODO fix imports (currently static imports are required!)
        __import__(f'{app_name}.cogs', fromlist=f'{cog}')
        # TODO find solution without eval()
        bot.add_cog(eval(cog)(bot))

