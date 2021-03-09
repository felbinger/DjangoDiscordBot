from django.contrib import admin

from .models import Service, Ticket, Message


class MessageInLine(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('from_team', 'content',)
    readonly_fields = ('from_team',)


class TicketAdmin(admin.ModelAdmin):
    inlines = (
        MessageInLine,
    )


admin.site.register(Service)
admin.site.register(Ticket, TicketAdmin)
