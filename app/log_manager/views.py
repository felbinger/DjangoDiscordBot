# from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpRequest  # , HttpResponseForbidden
from django.shortcuts import render
from uuid import uuid4

from log_manager.models import Transcript
# from user_manager.models import DiscordUser


@login_required(login_url="/login")
def show(request: HttpRequest, transcript_id: uuid4):
    # FIXME should only work with auth
    # if not request or not request.user or not request.user.is_authenticated:
    #     return HttpResponseForbidden()

    transcript = Transcript.objects.filter(public_id=transcript_id).first()

    if not transcript:
        return HttpResponseNotFound()

    # discord_user = DiscordUser.objects.filter(user=request.user).first()
    # if not discord_user.user.groups.filter(name=settings.DISCORD_LOGGING_REQUIRED_GROUP).exists():
    #     return HttpResponseForbidden()

    return render(request, f'transcripts/{transcript_id}.html')
