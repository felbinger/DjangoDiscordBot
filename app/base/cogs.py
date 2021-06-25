from typing import Optional

from asgiref.sync import sync_to_async
from discord import Guild, Role, Member
from discord.ext import commands
from discord.ext.commands import Cog, Bot

from base.models import User, Group

__all__ = ["Base"]


@sync_to_async
def _create_or_update_user(user_id: int, username: str, is_bot: bool):
    user, created = User.objects.get_or_create(discord_id=user_id)
    if user:
        user.username = username
        user.is_bot = is_bot
        user.save()

    # add user to @everyone discord group
    if grp := Group.objects.filter(name="@everyone").first():
        grp.user_set.add(User.objects.filter(username=username).first())


@sync_to_async
def _create_or_update_group(group_id: int, group_name: str):
    grp, _ = Group.objects.get_or_create(discord_id=group_id)
    if grp:
        grp.name = group_name
        grp.save()


@sync_to_async
def _delete_group(group_id: int):
    if grp := Group.objects.filter(discord_id=group_id).first():
        grp.delete()


@sync_to_async
def _user_add_group(user_id: str, role_id: str):
    user = User.objects.filter(discord_id=user_id).first()
    grp = Group.objects.filter(discord_id=role_id).first()
    if user and grp:
        grp.user_set.add(user)


@sync_to_async
def _user_remove_group(user_id: str, role_id: str):
    user = User.objects.filter(discord_id=user_id).first()
    grp = Group.objects.filter(discord_id=role_id).first()
    if not user or not grp:
        return
    grp.user_set.remove(user)


class Base(Cog, name='base'):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild: Optional[Guild] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: Optional[Guild] = self.bot.guilds[0]
        for role in self.guild.roles:
            await _create_or_update_group(role.id, role.name)

        for member in self.guild.members:
            await _create_or_update_user(member.id, member.name, member.bot)
            for role in member.roles:
                await _user_add_group(member.id, role.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        await _create_or_update_user(member.id, member.name, member.bot)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        await _create_or_update_user(after.id, after.name, after.bot)

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

    # trigger('base', 'add_member_to_role', 'user_id', 'role_id')
    async def add_member_to_role(self, member_id: int, role_id: int):
        self.guild.get_member(member_id).add_roles(role_id)

    # trigger('base', 'remove_member_from_role', 'user_id', 'role_id')
    async def remove_member_from_role(self, member_id: int, role_id: int):
        self.guild.get_member(member_id).remove_roles(role_id)
