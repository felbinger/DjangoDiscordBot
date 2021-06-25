from django.contrib import admin
from django.contrib.auth.models import Group as DefaultGroup
from django.forms import ModelForm, IntegerField, TextInput
from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken, IDToken

from .models import User, Group, Settings


class UserAdminForm(ModelForm):
    """
    show normal input field instead of integer input for the discord id field
    """
    discord_id = IntegerField(widget=TextInput, required=False, disabled=True)
    model = User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'discord_id', 'is_bot', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    form = UserAdminForm


class GroupAdminForm(ModelForm):
    """
    show normal input field instead of integer input for the discord id field
    """
    discord_id = IntegerField(widget=TextInput, required=False, disabled=True)
    model = Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'discord_id')
    form = GroupAdminForm


@admin.register(Settings)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')


# remove default group model
admin.site.unregister(DefaultGroup)

# remove oauth provider from admin
admin.site.unregister(AccessToken)
admin.site.unregister(Application)
admin.site.unregister(Grant)
admin.site.unregister(RefreshToken)
admin.site.unregister(IDToken)
