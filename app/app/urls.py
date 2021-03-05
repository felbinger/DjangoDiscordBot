from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

urlpatterns = [
    path('', include('user_manager.urls')),
    path('admin/', admin.site.urls, name='admin'),
    path('login/', LoginView.as_view(template_name='login.html'),  name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('transcripts/', include('log_manager.urls'), name='transcripts'),
]

admin.site.site_title = 'Django Discord Bot Template'
