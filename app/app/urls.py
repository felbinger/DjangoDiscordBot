from django.contrib import admin
from django.urls import path, include

# TODO remove for productive...
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include(('user_manager.urls', 'user_manager',), namespace='user_manager')),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include(('django.contrib.auth.urls', 'accounts',), namespace='accounts')),
    path('transcripts/', include(('log_manager.urls', 'transcripts',), namespace='transcripts')),
    path('support/', include(('support.urls', 'support',), namespace='support')),
] + staticfiles_urlpatterns()

admin.site.site_title = 'Django Discord Bot Template'
