from discord import Intents
from discord.ext.commands import Bot
from os import environ
from user_manager.cogs import UserManager
from log_manager.cogs import LogManager

bot = Bot(
    # TODO should be configurable using settings.py
    command_prefix=environ.get('DISCORD_BOT_PREFIX', ''),
    case_insensitive=True,
    # TODO should be configurable using settings.py
    description="Django Discord Bot Template",
    intents=(Intents.all()),
)

# for cog in [UserManager, LogManager]:
#     bot.add_cog(partial(cog, args=bot))

# TODO should be automatically configured using INSTALLED_APPS in settings.py
bot.add_cog(UserManager(bot))
bot.add_cog(LogManager(bot))
