import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect

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
            discord_notifications = False
            if 'discord_notifications' in request.POST and request.POST['discord_notifications'] == 'on':
                discord_notifications = True
            ticket = Ticket(
                owner=request.user,
                subject=request.POST['subject'],
                service=Service.objects.filter(id=request.POST['service']).first(),
                description=request.POST['description'],
                priority=request.POST['priority'],
                discord_notifications=discord_notifications,
            )
            ticket.save()
            # flash message, clear form by sending an new/empty one
            return redirect('support:overview')
        else:
            messages.error(request, 'Something went wrong...')

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
