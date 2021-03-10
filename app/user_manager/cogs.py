from typing import Optional

from asgiref.sync import sync_to_async
from discord import Guild, Role, Member
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from django.contrib.auth.models import User, Group

from user_manager.models import DiscordUser, DiscordGroup

__all__ = ["UserManager"]


def _create_or_update(outer_cls, outer_attr, inner_cls, inner_attr, discord_id, name):
    outer_obj, outer_created = outer_cls.objects.get_or_create(discord_id=discord_id)
    if outer_created or not hasattr(outer_obj, outer_attr):
        inner_obj, _ = inner_cls.objects.get_or_create(**{inner_attr: name})
        setattr(outer_obj, outer_attr, inner_obj)
    setattr(getattr(outer_obj, outer_attr), inner_attr, name)
    getattr(outer_obj, outer_attr).save()
    outer_obj.save()


@sync_to_async
def _create_or_update_user(user_id: int, username: str):
    _create_or_update(DiscordUser, "user", User, "username", user_id, username)

    if grp := Group.objects.filter(name="@everyone").first():
        grp.user_set.add(User.objects.filter(username=username).first())


@sync_to_async
def _create_or_update_group(group_id: int, group_name: str):
    _create_or_update(DiscordGroup, "group", Group, "name", group_id, group_name)


@sync_to_async
def _delete_group(group_id: int):
    discord_group = DiscordGroup.objects.filter(discord_id=group_id).first()
    if discord_group.group:
        discord_group.group.delete()
    discord_group.delete()


@sync_to_async
def _user_add_group(user_id: str, role_id: str):
    discord_user = DiscordUser.objects.filter(discord_id=user_id).first()
    discord_group = DiscordGroup.objects.filter(discord_id=role_id).first()
    discord_group.group.user_set.add(discord_user.user)


@sync_to_async
def _user_remove_group(user_id: str, role_id: str):
    discord_user = DiscordUser.objects.filter(discord_id=user_id).first()
    discord_group = DiscordGroup.objects.filter(discord_id=role_id).first()
    if not discord_user or not discord_group:
        return
    discord_group.group.user_set.remove(discord_user.user)


class UserManager(Cog, name='user_manager'):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild: Optional[Guild] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: Optional[Guild] = self.bot.guilds[0]
        for role in self.guild.roles:
            await _create_or_update_group(role.id, role.name)

        for member in self.guild.members:
            await _create_or_update_user(member.id, member.name)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        await _create_or_update_user(member.id, member.name)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        await _create_or_update_user(after.id, after.name)

        # user got a new role
        if len(before.roles) < len(after.roles):
            role = next(role for role in after.roles if role not in before.roles)
            await _user_add_group(before.id, role.id)

        # user has been removed from a role
        if len(before.roles) > len(after.roles):
            role = next(role for role in before.roles if role not in after.roles)
            await _user_remove_group(before.id, role.id)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: Role):
        await _create_or_update_group(role.id, role.name)

    @commands.Cog.listener()
    async def on_guild_role_update(self, _: Role, after: Role):
        await _create_or_update_group(after.id, after.name)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        await _delete_group(role.id)
