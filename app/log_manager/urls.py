from django.urls import path

from . import views

urlpatterns = [
    path('transcripts', views.TranscriptsView.as_view(), name='show_all'),
    path('transcript/<uuid:transcript_id>', views.TranscriptView.as_view(), name='show'),
]
