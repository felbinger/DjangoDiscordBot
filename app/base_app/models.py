from django.db import models
from django.contrib.auth.models import Group, User


class DiscordUser(models.Model):
    class Meta:
        verbose_name = "User"

    discord_id = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="django_user", blank=True, null=True
    )

    def __str__(self):
        ret = str(self.discord_id)
        if self.user:
            ret = f"[{self.discord_id}] {self.user.username}"
        return ret


class DiscordGroup(models.Model):
    class Meta:
        verbose_name = "Group"

    discord_id = models.IntegerField()
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        related_name="django_group", blank=True, null=True
    )

    def __str__(self):
        ret = str(self.discord_id)
        if self.group:
            ret = f"[{self.discord_id}] {self.group.name}"
        return ret
