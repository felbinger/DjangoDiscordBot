from django.db import models
from django.contrib.auth.models import Group, User


class Settings(models.Model):

    class Meta:
        verbose_name_plural = "Settings"

    key = models.CharField(max_length=128)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.key}: {self.value}"


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
