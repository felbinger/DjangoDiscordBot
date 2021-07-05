from django.db import models
from django.contrib.auth.models import AbstractUser, Group as DefaultGroup


class Settings(models.Model):

    class Meta:
        verbose_name_plural = "Settings"

    key = models.CharField(max_length=128)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.key}: {self.value}"


class User(AbstractUser):
    discord_id = models.IntegerField(null=True, blank=True, unique=True)
    is_bot = models.BooleanField(default=False)


# TODO group names are unique - discord role names aren't
# TODO discord roles are sorted - django groups aren't
class Group(DefaultGroup):
    discord_id = models.IntegerField(null=True, blank=True, unique=True)
