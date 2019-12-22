import json
import requests
import uuid
import xmltodict
from rest_framework import status

from django.db import models

from .exceptions import ProviderURLException


class ProviderResource(models.Model):
    """
    Resource of a Provider
    """
    JSON = 1
    XML = 2

    RESOURCE_TYPES = (
        (JSON, 'JSON'),
        (XML, 'XML')
    )

    url = models.URLField()
    _data = None
    _resource = None
    _resource_type = None

    def get_external_resource(self):
        """
        Get resource from the provider url
        """
        response = requests.get(self.url)
        if response.status_code != status.HTTP_200_OK:
            raise ProviderURLException("Error in provider URL")

        try:
            self._resource = json.loads(response.text)
            self._resource_type = self.JSON
        except ValueError:
            pass

        try:
            self._resource = xmltodict.parse(response.text)
            self._resource_type = self.XML
        except TypeError:
            raise ValueError

    def adapt_resource(self):
        """
        Adapt the resource data to the standard form
        """
        if not self._resource:
            self.get_external_resource()

    def save_resource(self):
        """
        Save the Provider Resource data
        """
        if not self._data:
            self.adapt_resource()

        for event in self._data:
            events = self.provider.events.filter(
                provider_event_id=event['provider_event_id']
            )
            if events.exists():
                provider_event = events.first()
            else:
                provider_event = Event(
                    title=event['title'],
                    active=event['active'],
                    provider=self.provider,
                    provider_event_id=event['provider_event_id']
                )
                provider_event.save()

            for date in event['dates']:
                dates = event.dates.filter(
                    provider_date_id=date['provider_date_id']
                )
                if dates.exists():
                    event_date = dates.first()
                else:
                    event_date = EventDate(
                        event=provider_event,
                        provider_date_id=date['provider_date_id']
                    )

                event_date.date = date['date']
                event_date.sale_start_date = date['sale_start_date']
                event_date.event_date = date['sale_end_date']
                date.save()

                for zone in date['zones']:
                    zones = Zone.objects.filter(
                        provider_zone_id=zone['provider_zone_id']
                    )
                    if zones.exists():
                        event_zone = zones.first()
                    else:
                        event_zone = Zone(
                            name=zone['name'],
                            price=zone['price'],
                            numbered=zone['numbered'],
                            date=event_date,
                            provider_zone_id=zone['provider_zone_id'],
                        )

                    event_zone.rest = zones['rest']
                    event_zone.save()


class Provider(models.Model):
    """
    Provider definition
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=25)
    provider_resource = models.OneToOneField(
        ProviderResource,
        on_delete=models.CASCADE,
        related_name='provider'
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.name

    def get_external_events(self):
        """
        Get provider events and save
        """
        self.provider_resource.save_resource()


class Event(models.Model):
    """
    Event definition
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    provider = models.ForeignKey(
        'Provider',
        related_name='events',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    provider_event_id = models.PositiveIntegerField()

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['provider'])]

    def __str__(self):
        return self.title


class EventDate(models.Model):
    """
    Event Date definition
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date = models.DateTimeField()
    sale_start_date = models.DateTimeField()
    sale_end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    event = models.ForeignKey(
        'Event',
        related_name='dates',
        on_delete=models.CASCADE,
    )
    provider_date_id = models.PositiveIntegerField()

    class Meta:
        ordering = ['date']
        indexes = [models.Index(fields=['event'])]

    def __str__(self):
        return "{}, {}".format(self.event, str(self.date))

    def is_sold_out(self):
        """
        Get if the event is totally sold out
        """
        return not self.zones.filter(sold__gt=0).exists()


class Zone(models.Model):
    """
    Event Zone definition
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=25)
    capacity = models.PositiveIntegerField()
    rest = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    numbered = models.BooleanField(default=False)
    date = models.ForeignKey(
        'EventDate',
        related_name='zones',
        on_delete=models.CASCADE,
    )
    provider_zone_id = models.PositiveIntegerField()

    class Meta:
        ordering = ['date']
        indexes = [models.Index(fields=['date'])]

    def __str__(self):
        return "{}, {}".format(self.date, self.name)

