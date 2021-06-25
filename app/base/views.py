from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render, redirect
import requests
from django.urls import reverse

from base.models import User


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def discord_auth(request: HttpRequest) -> HttpResponse:
    return redirect(settings.OAUTH_URL)


def discord_auth_redirect(request: HttpRequest) -> HttpResponse:
    if 'code' not in request.GET:
        return HttpResponseBadRequest()

    auth_resp = requests.post("https://discord.com/api/oauth2/token", data={
        "client_id": settings.OAUTH_CLIENT_ID,
        "client_secret": settings.OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": request.GET.get('code'),
        "redirect_uri": f"{settings.SCHEMA}://{settings.PUBLIC_URL}{reverse('base:discord_oauth_redirect')}",
        "scope": "identify"
    }, headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    if not auth_resp.ok:
        return HttpResponseBadRequest()

    identity_resp = requests.get('https://discord.com/api/v6/users/@me', headers={
        'Authorization': f'{auth_resp.json().get("token_type")} {auth_resp.json().get("access_token")}'
    })
    if not identity_resp.ok:
        return HttpResponseBadRequest()

    user = User.objects.filter(discord_id=identity_resp.json().get('id')).first()
    if not user:
        return HttpResponseNotFound("You are not on the server")

    login(request, user, backend="oauth2_provider.backends.OAuth2Backend")

    return redirect(settings.LOGIN_REDIRECT_URL)
