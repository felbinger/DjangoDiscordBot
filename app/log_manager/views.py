from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render
from uuid import uuid4

from log_manager.models import Transcript
from user_manager.models import DiscordUser


@login_required(login_url="/login")
def show(request, transcript_id: uuid4):
    if not request or not request.user or not request.user.is_authenticated:
        return HttpResponseForbidden()

    transcript = Transcript.objects.filter(public_id=transcript_id).first()

    if not transcript:
        return HttpResponseNotFound()

    user = DiscordUser.objects.filter(user=request.user).first()

    # if user does not belong to team (does not have staff status (for django native users) or team discord role)
    if not request.user.is_staff and \
            (user and not user.user.groups.filter(name=settings.DISCORD_LOGGING_REQUIRED_GROUP).exists()):
        return HttpResponseForbidden()

    return render(request, f'transcripts/{transcript_id}.html')
