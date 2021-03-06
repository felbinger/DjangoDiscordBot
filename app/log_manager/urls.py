from django.urls import path

from . import views

urlpatterns = [
    path('<uuid:transcript_id>', views.show, name='show'),
]
