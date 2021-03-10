# django to discord event

from app.asgi import loop
from app.bot import bot


def trigger(cog_name: str, func_name, *args, **kwargs):
    cog = bot.get_cog(cog_name)
    if not hasattr(cog, func_name):
        raise NameError(f"{func_name} does not exist in cog: {cog_name}")
    loop.create_task(getattr(cog, func_name)(*args, **kwargs))
