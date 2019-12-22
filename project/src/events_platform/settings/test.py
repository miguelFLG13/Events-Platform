from .base import *

DEBUG = True

ALLOWED_HOSTS = [LOCAL_IP]

ROOT_URLCONF = 'events_platform.urls.urls'

CACHES = {
    'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}
