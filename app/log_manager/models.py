from django.db import models
from django.utils import timezone

from uuid import uuid4

from user_manager.models import DiscordGroup, DiscordUser


class Transcript(models.Model):
    public_id = models.UUIDField(default=uuid4)
    channel_name = models.CharField(max_length=120, blank=False, null=False)
    created = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_by = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, related_name="created_by_user")
    notes = models.TextField(max_length=8192, blank=True, null=True)

    # the member of the configure group are able to access the transcript (e. g. everyone / team)
    readable_by = models.ForeignKey(DiscordGroup, on_delete=models.CASCADE, related_name="transcript_readable_by_group")

    def __str__(self):
        return f'{self.public_id} ({self.channel_name}, {self.created.strftime("%Y-%m-%d %H:%M:%S")})'
