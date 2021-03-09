from typing import Optional
from discord import Guild
from discord.ext.commands import Cog, Bot
from discord.ext import commands

__all__ = ["SupportManager"]

from django.conf import settings


class SupportManager(Cog, name='support_manager'):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild: Optional[Guild] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: Optional[Guild] = self.bot.guilds[0]

    async def send_message(self, content):
        await self.guild.get_channel(settings.DISCORD_LOGGING_CHANNEL).send(content)

    async def send_dm(self, member_id, content: str):
        await self.guild.get_member(member_id).send(content)
