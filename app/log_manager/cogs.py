from pathlib import Path
from typing import List, Optional, Dict
import re
from asgiref.sync import sync_to_async
from discord import Embed, Guild, Reaction, Member
from discord.ext.commands import Cog, command, Context, Bot
from django.conf import settings
from discord.ext import commands
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from markupsafe import Markup

from log_manager.models import Transcript
from user_manager.models import DiscordGroup, DiscordUser


@sync_to_async
def _create_transcript(channel_name: str, created_by: Member, guild_name: str, guild_icon: str, messages: List[Dict]):
    transcript = Transcript(
        channel_name=channel_name,
        created_by=DiscordUser.objects.filter(user__username=created_by.name).first(),
        readable_by=DiscordGroup.objects.filter(group__name=settings.DISCORD_LOGGING_REQUIRED_GROUP).first(),
    )
    transcript.save()

    templates = Path(settings.TEMPLATES[0]["DIRS"][0])
    transcripts = templates.joinpath('transcripts')
    if not transcripts.is_dir():
        transcripts.mkdir(parents=True)
    filename = Path(f'{transcripts}/{transcript.public_id}.html')

    jinja_env = Environment(loader=FileSystemLoader(templates))
    jinja_env.filters['regexr'] = lambda s: re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', s)
    jinja_env.filters['markdown'] = lambda text: Markup(Markdown(extensions=['meta']).convert(text))

    template = jinja_env.get_template('transcript.html')

    rendered_transcript = template.render(
        guild={
            "name": guild_name,
            "icon": guild_icon
        },
        channel_name=channel_name,
        messages=messages
    )

    with filename.open('w') as f:
        f.write(rendered_transcript)

    return transcript.public_id


class LogManager(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.guild: Optional[Guild] = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: Optional[Guild] = self.bot.guilds[0]

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

        if not message_amount:
            message_amount = settings.DISCORD_LOGGING_TRANSCRIPTS_DEFAULT

        if type(message_amount) == str:
            await ctx.send(
                f"Not a number, using default: {settings.DISCORD_LOGGING_TRANSCRIPTS_DEFAULT}"
            )
            message_amount = settings.DISCORD_LOGGING_TRANSCRIPTS_DEFAULT

        if int(message_amount) > settings.DISCORD_LOGGING_TRANSCRIPTS_MAX:
            message_amount = settings.DISCORD_LOGGING_TRANSCRIPTS_MAX
            await ctx.send(
                f"Maximum amount of messages have been limited to: {settings.DISCORD_LOGGING_TRANSCRIPTS_MAX}"
            )

        # create list of messages
        messages = list()
        async for msg in ctx.channel.history(limit=message_amount, oldest_first=False):
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

        # create transcript meta data and html file
        public_id = await _create_transcript(
            guild_name=self.guild.name,
            guild_icon=self.guild.icon_url,
            channel_name=ctx.message.channel,
            created_by=ctx.message.author,
            messages=messages,
        )

        url = f'http://127.0.0.1:8000/transcripts/{public_id}'

        # confirm creation is completed and send user the link
        await ctx.send(
            embed=Embed(
                title="Transcript has been created!",
                description=f"The latest {message_amount} message have been saved to: {url}"
            )
        )
