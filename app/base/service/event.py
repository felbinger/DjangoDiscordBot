from django.dispatch import receiver

from app.asgi import loop
from app.bot import bot

from ..models import Group
from ..service.signals import group_created, group_deleted


def trigger(cog_name: str, func_name, *args, **kwargs):
    cog = bot.get_cog(cog_name)
    if not hasattr(cog, func_name):
        raise NameError(f"{func_name} does not exist in cog: {cog_name}")
    loop.create_task(getattr(cog, func_name)(*args, **kwargs))


# DJANGO ADMIN: CREATE GRP (ID UNKNOWN) -> DISCORD CREATE ROLE (GEN ID) -> DJANGO GRP->ID = ID
@receiver(group_created, sender=Group)
def create_or_update_group_handler(sender, **kwargs):
    grp = kwargs['instance']
    if grp and kwargs['created']:
        trigger('base', 'create_role', grp.name)
    else:
        trigger('base', 'update_role', grp.discord_id, grp.name)


@receiver(group_deleted, sender=Group)
def delete_group_handler(sender, **kwargs):
    grp = kwargs['instance']
    if grp:
        trigger('base', 'delete_role', grp.discord_id)


# @receiver(post_save, sender=User)
# def create_or_update_user_handler(sender, **kwargs):
#     user = kwargs['instance']
#     if user.discord_id and not kwargs['created']:
#         # TODO how to get role id - changes in user.groups
#         pass
#         # trigger('base', 'add_member_to_role', user.discord_id, 'role_id')
#         # trigger('base', 'remove_member_from_role', 'user_id', 'role_id')
