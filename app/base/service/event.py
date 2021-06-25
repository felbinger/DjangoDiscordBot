# django to discord event

from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save

from app.asgi import loop
from app.bot import bot

from django.dispatch import receiver


def trigger(cog_name: str, func_name, *args, **kwargs):
    cog = bot.get_cog(cog_name)
    if not hasattr(cog, func_name):
        raise NameError(f"{func_name} does not exist in cog: {cog_name}")
    loop.create_task(getattr(cog, func_name)(*args, **kwargs))


# think about updating the update method of the model...
# @receiver(post_save, sender=Group)
# def my_handler(sender, **kwargs):
#     print(sender, kwargs)
#
#
# @receiver(post_save, sender=User)
# def my_handler(sender, **kwargs):
#     print(sender, kwargs)
