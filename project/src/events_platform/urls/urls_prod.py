from django.urls import path
from django.conf.urls import include


urlpatterns = [
    path('v1/', include('events_platform.urls.base_urls')),
]
