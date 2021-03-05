from django.contrib import admin
from django.contrib.auth.models import User, Group

from .models import DiscordGroup, DiscordUser


class DiscordUserAdmin(admin.ModelAdmin):
    readonly_fields = ("discord_id", "user",)


class DiscordGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("discord_id", "group",)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(DiscordUser, DiscordUserAdmin)
admin.site.register(DiscordGroup, DiscordGroupAdmin)
