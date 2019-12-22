from .base import *

DEBUG = True

ALLOWED_HOSTS = [LOCAL_IP, 'web']

ROOT_URLCONF = 'events_platform.urls.urls_local'

CACHES = {
    'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}
