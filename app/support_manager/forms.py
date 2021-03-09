from django import forms
from django.utils.translation import gettext as _
from .models import Service, Ticket


class TicketForm(forms.Form):
    subject = forms.CharField(max_length=128, widget=forms.TextInput(attrs={
        'placeholder': _('Subject'),
        'class': 'form-control',
    }), required=True)

    service = forms.ModelChoiceField(
        widget=forms.Select(attrs={
            'placeholder': _('Service'),
            'class': 'form-control',
        }),
        queryset=Service.objects.all(),
        required=True
    )

    description = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': _('Description'),
        'class': 'form-control',
    }), required=True)

    priority = forms.ChoiceField(
        widget=forms.Select(attrs={
            'placeholder': _('Priority'),
            'class': 'form-control',
        }),
        choices=Ticket.PRIORITIES,
        required=True
    )

    discord_notifications = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
