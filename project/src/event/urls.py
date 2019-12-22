from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import EventListView

urlpatterns = [
    path(
        '',
        cache_page(settings.CACHE_DEFAULT_TIME)(EventListView.as_view()),
        name='events'
    ),
]
