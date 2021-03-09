from typing import Optional

from asgiref.sync import sync_to_async
from discord import Guild, Role, Member
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from django.contrib.auth.models import User, Group

from user_manager.models import DiscordUser, DiscordGroup

__all__ = ["UserManager"]


@sync_to_async
def _create_or_update_user(user_id: int, username: str):
    discord_user, discord_user_created = DiscordUser.objects.get_or_create(discord_id=user_id)
    if discord_user_created or not discord_user.user:
        user, _ = User.objects.get_or_create(username=username)
        discord_user.user = user
    discord_user.user.username = username
    discord_user.user.save()
    discord_user.save()


@sync_to_async
def _create_or_update_group(group_id: int, group_name: str):
    discord_group, discord_group_created = DiscordGroup.objects.get_or_create(discord_id=group_id)
    if discord_group_created or not discord_group.group:
        group, _ = Group.objects.get_or_create(name=group_name)
        discord_group.group = group
    discord_group.group.name = group_name
    discord_group.group.save()
    discord_group.save()


@sync_to_async
def _delete_group(group_id: int):
    discord_group = DiscordGroup.objects.filter(discord_id=group_id).first()
    if discord_group.group:
        discord_group.group.delete()
    discord_group.delete()


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
    async def on_member_update(self, _: Member, after: Member):
        await _create_or_update_user(after.id, after.name)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: Role):
        await _create_or_update_group(role.id, role.name)

    @commands.Cog.listener()
    async def on_guild_role_update(self, _: Role, after: Role):
        await _create_or_update_group(after.id, after.name)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        await _delete_group(role.id)
