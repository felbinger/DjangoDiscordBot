from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseNotFound, HttpResponse, HttpRequest
from uuid import uuid4

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from log_manager.models import Transcript


class TranscriptsView(View):

    @method_decorator(login_required)
    @method_decorator(permission_required('log_manager.view_transcript'))
    def get(self, request: HttpRequest):
        return render(request, "transcripts.html", context={
            "transcripts": [
                {
                    "id": t.public_id,
                    "channel_name": t.channel_name,
                    "created": t.created,
                } for t in Transcript.objects.all()
            ]
        })


class TranscriptView(View):
    @method_decorator(login_required)
    @method_decorator(permission_required('log_manager.view_transcript'))
    def get(self, request: HttpRequest, transcript_id: uuid4):
        transcript = Transcript.objects.filter(public_id=transcript_id).first()
        f = Path(f'{settings.BASE_DIR}/media/transcripts/{transcript_id}.html')

        if not transcript or not f.is_file():
            return HttpResponseNotFound()

        with f.open('r') as f:
            return HttpResponse(f.read())

    @method_decorator(login_required)
    @method_decorator(permission_required('log_manager.delete_transcript'))
    def delete(self, request: HttpRequest, transcript_id: uuid4):
        transcript = Transcript.objects.filter(public_id=transcript_id).first()

        f = Path(f'{settings.BASE_DIR}/media/transcripts/{transcript_id}.html')
        if f.is_file():
            f.unlink(missing_ok=True)

        if not transcript:
            return HttpResponseNotFound()

        transcript.delete()
        return HttpResponse(status=204)
