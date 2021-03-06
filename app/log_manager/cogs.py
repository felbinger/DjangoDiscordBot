from pathlib import Path
from typing import List, Optional, Dict
import re
from asgiref.sync import sync_to_async
from discord import Embed, Guild, Reaction, Member
from discord.abc import PrivateChannel
from discord.ext import commands
from discord.ext.commands import Cog, command, Context, Bot
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from base.service.settings import get_setting
from log_manager.models import Transcript
from base.models import User

__all__ = ["LogManager"]


@sync_to_async
def _create_transcript(channel_name: str, created_by: Member, guild_name: str, guild_icon: str, messages: List[Dict]):
    transcript = Transcript(
        channel_name=channel_name,
        created_by=User.objects.filter(username=created_by.name).first(),
    )
    transcript.save()

    transcript_content = render_to_string('transcript.html', context={
        "guild": {
            "name": guild_name,
            "icon": guild_icon,
        },
        "channel_name": channel_name,
        "messages": messages,
    })

    transcripts = Path(settings.MEDIA_ROOT).joinpath('transcripts')
    with Path(f'{transcripts}/{transcript.public_id}.html').open('w') as f:
        f.write(transcript_content)

    return transcript.public_id


@sync_to_async
def _has_create_transcripts_permission(username) -> bool:
    user = User.objects.filter(username=username).first()
    return user and user.has_perm('log_manager.add_transcript')


class LogManager(Cog, name="log_manager"):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild: Optional[Guild] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: Optional[Guild] = self.bot.guilds[0]

        transcripts = Path(settings.MEDIA_ROOT).joinpath('transcripts')
        if not transcripts.is_dir():
            transcripts.mkdir(parents=True)

    def add_mention_suffix(self, s):
        def get_member(_id):
            member = self.guild.get_member(int(_id))
            if member:
                return member.name
            return "unknown"

        if isinstance(s, str):
            y = re.sub(r'<@\!?(\d*?)>', lambda x: f"<@{x.group(1)}> ({get_member(x.group(1))})", s)
        else:
            y = ""
        return y

    @command(name="save", aliases=["s"])
    async def save_transcript(self, ctx: Context, message_amount=None):
        def get_reaction_url(reaction: Reaction) -> str:
            # TODO check if length can be longer than 1
            if isinstance(reaction.emoji, str) and len(reaction.emoji) == 1:
                return f"https://twemoji.maxcdn.com/2/72x72/{hex(ord(str(reaction.emoji)))[2:]}.png"
            else:
                return reaction.emoji.url

        if ctx.message.author.bot:
            return

        if not await _has_create_transcripts_permission(ctx.message.author.name):
            await ctx.send(
                _("You aren't allowed to create transcripts!")
            )
            return

        if isinstance(ctx.channel, PrivateChannel):
            await ctx.send(
                _("You can't create transcripts of dm channel!")
            )
            return

        db_message_amount = await get_setting("transcript_amount")
        if not message_amount:
            message_amount = int(db_message_amount) or 100

        if type(message_amount) == str and not message_amount.isdigit():
            await ctx.send(
                _(f"Not a number, using default: {db_message_amount}")
            )
            message_amount = int(db_message_amount) or 100

        if int(message_amount) > settings.DISCORD_LOGGING_TRANSCRIPTS_MAX:
            message_amount = settings.DISCORD_LOGGING_TRANSCRIPTS_MAX
            await ctx.send(
                _(f"Maximum amount of messages have been limited to: {settings.DISCORD_LOGGING_TRANSCRIPTS_MAX}")
            )

        # create list of messages
        messages = list()
        message_counter = 0
        async for msg in ctx.channel.history(limit=int(message_amount), oldest_first=False):
            message_counter += 1
            messages.append({
                "id": msg.id,
                "bot": msg.author.bot,
                "attachments": msg.attachments,
                "embeds": [{
                    "title": self.add_mention_suffix(embed.title),
                    "description": self.add_mention_suffix(embed.description)
                    if isinstance(embed.description, str) else "",
                    "color": embed.color,
                    "thumbnail": embed.thumbnail if isinstance(embed.thumbnail, str) else "",
                    "fields": [{
                        "title": self.add_mention_suffix(f.name),
                        "description": self.add_mention_suffix(f.value),
                    } for f in embed.fields]
                } for embed in msg.embeds],
                "author": {
                    "id": msg.author.id,
                    "name": msg.author.display_name,
                    "avatar": msg.author.avatar_url,
                },
                "timestamp": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "content": self.add_mention_suffix(msg.content),
                "reactions": [
                    {
                        "emoji": reaction.emoji,
                        "count": reaction.count,
                        "src": get_reaction_url(reaction)
                    } for reaction in msg.reactions
                ]
            })

        if not self.guild:
            await ctx.send(
                _("Bot hasn't fully started yet, try again later!")
            )
            return

        # create transcript meta data and html file
        public_id = await _create_transcript(
            guild_name=self.guild.name,
            guild_icon=self.guild.icon_url,
            channel_name=ctx.message.channel,
            created_by=ctx.message.author,
            messages=messages,
        )

        path = reverse('log_manager:show', kwargs={"transcript_id": public_id})
        url = f'{settings.SCHEMA}://{settings.PUBLIC_URL}{path}'

        # confirm creation is completed and send user the link
        await ctx.send(
            embed=Embed(
                title=_("Transcript has been created!"),
                description=_(f"The latest {message_counter} message have been saved to: {url}")
            )
        )
