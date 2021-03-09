from django.urls import path

from .views import overview, edit, new, send_message


urlpatterns = [
    path('', overview, name='overview'),
    path('new/', new, name='new'),
    path('edit/<int:ticket_id>', edit, name='edit'),
    path('send/<int:ticket_id>', send_message, name='send_message')
]
