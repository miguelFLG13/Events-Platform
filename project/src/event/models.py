import uuid

from django.db import models


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
    events_url = models.URLField()

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.name


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
        return not self.zones.filter(sold_out=False).exists()


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
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    numbered = models.BooleanField(default=False)
    sold_out = models.BooleanField(default=False)
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
