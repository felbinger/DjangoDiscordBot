import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from base.models import User
from base.service.event import trigger

from .models import Ticket, Service, Message
from .forms import TicketForm


@login_required
def overview(request: WSGIRequest):
    data = {
        "tickets": [
            {
                "id": t.id,
                "subject": t.subject,
                "service": t.service.name,
                "status": t.STATES[t.status][1],
            } for t in Ticket.objects.filter(owner=request.user).all()
        ],
    }
    return render(request, 'overview.html', context=data)


@login_required
def new(request: WSGIRequest):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():

            discord_notifications = 'discord_notifications' in request.POST \
                and request.POST['discord_notifications'] == 'on'

            ticket = Ticket(
                owner=request.user,
                subject=request.POST['subject'],
                service=Service.objects.filter(id=request.POST['service']).first(),
                description=request.POST['description'],
                priority=request.POST['priority'],
                discord_notifications=discord_notifications,
            )
            ticket.save()

            trigger(
                cog_name='support_manager',
                func_name='send_message',
                content=_(f"Ticket (#{ticket.id}) has been created!")
            )

            if discord_notifications and (user := User.objects.filter(user=request.user).first()):
                trigger(
                    cog_name='support_manager',
                    func_name='send_dm',
                    member_id=user.discord_id,
                    content=_(f"You're ticket (#{ticket.id}) has been created, you will receive updates!")
                )

            return redirect('support_manager:overview')
        else:
            messages.error(request, _('Something went wrong...'))

    data = {
        "form": TicketForm()
    }
    return render(request, 'new.html', context=data)


@login_required
def edit(request: WSGIRequest, ticket_id: int):
    if not ticket_id or not (ticket := Ticket.objects.filter(id=ticket_id).first()):
        return HttpResponseNotFound()

    if not ticket.owner == request.user:
        return HttpResponseForbidden()

    data = {
        "services": [
            {
                "id": s.id,
                "name": s.name,
            } for s in Service.objects.all()
        ],
        "form": {
            "id": ticket_id,
            "subject": ticket.subject,
            "service": ticket.service,
            "priority": ticket.priority,
            "status": ticket.status,
            "description": ticket.description,
            "messages": [
                {
                    "id": m.id,
                    "team": m.from_team,
                    "content": m.content,
                    "created": m.created,
                } for m in Message.objects.filter(ticket=ticket).all()
            ]
        },
    }
    return render(request, 'edit.html', context=data)


@login_required
def send_message(request: WSGIRequest, ticket_id: int):
    data = json.loads(request.body)
    if 'content' not in data:
        return HttpResponseBadRequest()

    ticket = Ticket.objects.filter(id=ticket_id).first()

    if not ticket:
        return HttpResponseNotFound()

    # send forbidden if ticket is already closed
    if not ticket.owner == request.user or ticket.status == Ticket.STATES[2]:
        return HttpResponseForbidden()

    message = Message(
        ticket=ticket,
        content=data['content'],
        from_team=False,
    )
    message.save()

    return HttpResponse()
