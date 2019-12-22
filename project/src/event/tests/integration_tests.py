import uuid
from datetime import timedelta
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.utils import timezone

from ..models import Event, EventDate, Provider, Zone

from utils.test_services import generate_test_application, generate_test_token


class GetEventDatesTest(APITestCase):
    """ Test module for GET events API """

    def setUp(self):
        self.events_counter = 1
        self.event = mommy.make('event.event')
        self.date = mommy.make('event.eventdate', event=self.event)
        mommy.make('event.zone', date=self.date)
        self.url = reverse('events')

    def test_get_events_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.events_counter)
        self.assertEqual(uuid.UUID(response.data[0]['uuid']),
                         self.event.uuid)

    def test_get_events_data_range_valid(self):
        event = mommy.make('event.event')
        now = timezone.now()
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=2)
        date = mommy.make(
            'event.eventdate',
            event=self.event,
            sale_start_date=start_date,
            sale_end_date=end_date
        )
        mommy.make('event.zone', date=date)
        response = self.client.get(
            "{}?start_date={}&end_date={}".format(
                self.url,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.events_counter)
        self.assertEqual(uuid.UUID(response.data[0]['uuid']),
                         event.uuid)

    def test_get_events_data_out_range_valid(self):
        now = timezone.now()
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=2)
        response = self.client.get(
            "{}?start_date={}&end_date={}".format(
                self.url,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_events_inactive_event_valid(self):
        self.event.active = False
        self.event.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_events_inactive_date_valid(self):
        self.date.active = False
        self.date.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_events_incorrect_start_date_invalid(self):
        now = timezone.now()
        end_date = now + timedelta(days=2)
        response = self.client.get(
            "{}?start_date=sda&end_date={}".format(
                self.url,
                end_date.strftime("%Y-%m-%d")
            )
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_events_incorrect_end_date_invalid(self):
        now = timezone.now()
        start_date = now + timedelta(days=1)
        response = self.client.get(
            "{}?start_date={}&end_date=sda".format(
                self.url,
                start_date.strftime("%Y-%m-%d")
            )
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        Provider.objects.all().delete()
        Event.objects.all().delete()
        EventDate.objects.all().delete()
        Zone.objects.all().delete()
