from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

from .models import DiscordGroup, DiscordUser


class DiscordUserAdmin(admin.StackedInline):
    model = DiscordUser
    max_num = 0
    readonly_fields = ("discord_id",)


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'discord_id', 'is_staff')
    inlines = [DiscordUserAdmin]

    def discord_id(self, obj):
        discord_user = DiscordUser.objects.filter(user=obj).first()
        return discord_user.discord_id if discord_user else "-"


class DiscordGroupAdmin(admin.StackedInline):
    model = DiscordGroup
    max_num = 0
    readonly_fields = ("discord_id",)


class MyGroupAdmin(GroupAdmin):
    list_display = ('name', 'discord_id')
    inlines = [DiscordGroupAdmin]

    def discord_id(self, obj):
        discord_group = DiscordGroup.objects.filter(group=obj).first()
        return discord_group.discord_id if discord_group else "-"


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MyUserAdmin)
admin.site.register(Group, MyGroupAdmin)