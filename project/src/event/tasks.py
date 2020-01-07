from celery.schedules import crontab
from celery.task import periodic_task

from .models import Provider


@periodic_task(run_every=(crontab(minute='0', hour='3')), name="get_provider_events_task")
def get_provider_events_task():
    for provider in Provider.objects.all():
        provider.get_external_events()
