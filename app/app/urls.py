from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# TODO remove for productive...
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', include(('user_manager.urls', 'user_manager',), namespace='user_manager')),
    path('admin/', admin.site.urls, name='admin'),
    path('accounts/', include(('django.contrib.auth.urls', 'accounts',), namespace='accounts')),
    path('log/', include(('log_manager.urls', 'transcripts',), namespace='log_manager')),
    path('support/', include(('support_manager.urls', 'support_manager',), namespace='support_manager')),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_title = 'Django Discord Bot Template'
