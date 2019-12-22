from model_mommy import mommy

from django.conf import settings
from django.test import TestCase

from ..exceptions import ProviderURLException
from ..models import Event, EventDate, Provider, Zone


class ProviderResourceTestCase(TestCase):
    """
    Tests for ProviderResource class
    """
    def setUp(self):
        self.events_counter = 2
        self.event_dates_counter = 2
        self.zones_counter = 2
        self.provider_resource = mommy.make(
            'event.providerresource',
            url="{}/static/test.json".format(settings.LOCAL_IP)
        )
        mommy.make(
            'event.provider',
            provider_resource=provider_resource
        )

    def test_get_external_resource_json_valid(self):
        self.provider_resource.get_external_resource()
        with open("/static/test.json") as fl:
            file_text = fl.read()
        self.assertEqual(file_text, self.provider_resource.get_resource())

    def test_get_external_resource_xml_valid(self):
        self.provider_resource.url = "{}/static/test.xml".format(
            settings.LOCAL_IP
        )
        self.provider_resource.save()
        self.provider_resource.get_external_resource()

    def test_get_external_resource_incorrect_url_invalid(self):
        self.provider_resource.url = "{}/static/incorrect_url.json".format(
            settings.LOCAL_IP
        )
        self.provider_resource.save()
        with self.assertRaises(ProviderURLException):
            self.provider_resource.get_external_resource()

    def test_get_external_resource_incorrect_resource_invalid(self):
        self.provider_resource.url = "{}/static/test_incorrect_res.json".format(
            settings.LOCAL_IP
        )
        self.provider_resource.save()
        with self.assertRaises(ValueError):
            self.provider_resource.get_external_resource()

    def test_get_adapt_resource_default_valid(self):
        data = [
            {
                "provider_event_id": "291",
                "title": "Concert",
                "event": [
                    {
                        "date": "2019-06-30T21:00:00",
                        "provider_date_id": "291",
                        "sell_start_date": "2014-07-01T00:00:00",
                        "sell_end_date": "2019-06-30T20:00:00",
                        "zone": [
                            {
                                "provider_zone_id": "40",
                                "capacity": "243",
                                "name": "Platea",
                                "numbered": "true",
                                "sold": 243
                            },
                            {
                                "provider_zone_id": "38",
                                "capacity": "100",
                                "name": "test",
                                "numbered": "false"
                            }
                        ]
                    },
                    {
                        "date": "2019-06-30T21:00:00",
                        "provider_date_id": "292",
                        "sell_start_date": "2014-07-01T00:00:00",
                        "sell_end_date": "2019-06-30T20:00:00",
                    }
                ]
            },
            {
                "provider_event_id": "322",
                "title": "Theater"
            }
        ]

        self.provider_resource.adapt_resource()
        self.assertEqual(data, self.provider_resource.get_data())

    def test_get_adapt_resource_default_invalid(self):
        self.provider_resource.url = "{}/static/adapt_invalid.json".format(
            settings.LOCAL_IP
        )
        self.provider_resource.save()
        with self.assertRaises(KeyError):
            self.provider_resource.adapt_resource()

    def test_get_save_resource_valid(self):
        self.provider_resource.save()
        self.assertEqual(Event.objects.count(), self.events_counter)
        self.assertEqual(EventDate.objects.count(), self.event_dates_counter)
        self.assertEqual(Zone.objects.count(), self.zones_counter)

    def test_get_save_resource_invalid(self):
        with self.assertRaises(KeyError):
            self.provider_resource.save()

    def tearDown(self):
        Provider.objects.all().delete()
        Event.objects.all().delete()
