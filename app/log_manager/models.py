from django.db import models
from django.utils import timezone

from uuid import uuid4

from base_app.models import DiscordUser


class Transcript(models.Model):
    public_id = models.UUIDField(default=uuid4)
    channel_name = models.CharField(max_length=120, blank=False, null=False)
    created = models.DateTimeField(blank=True, null=True, default=timezone.now)
    created_by = models.ForeignKey(DiscordUser, on_delete=models.CASCADE, related_name="created_by_user")
    notes = models.TextField(max_length=8192, blank=True, null=True)

    def __str__(self):
        return f'{self.public_id} ({self.channel_name}, {self.created.strftime("%Y-%m-%d %H:%M:%S")})'
