from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Service(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATES = [
        (0, 'Open'),
        (1, 'Pending'),
        (2, 'Closed'),
    ]
    PRIORITIES = [
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="ticket_service")
    description = models.TextField()
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField('status', default=0, choices=STATES)
    priority = models.IntegerField('priority', default=0, choices=PRIORITIES)
    discord_notifications = models.BooleanField('discord_notifications', default=False)

    def __str__(self):
        info = "["

        # add status
        for _id, status in self.STATES:
            if _id != self.status:
                continue
            info += status
            break
        info += ", "

        # add priority
        for _id, priority in self.PRIORITIES:
            if _id != self.priority:
                continue
            info += priority
            break

        info += "]"
        return f'{info} {self.subject}'


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name="ticket_messages")
    from_team = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField()
