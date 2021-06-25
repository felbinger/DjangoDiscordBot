from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('oauth/', views.discord_auth, name='discord_oauth'),
    path('oauth/redirect', views.discord_auth_redirect, name='discord_oauth_redirect')
]
