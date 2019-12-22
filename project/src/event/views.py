from rest_framework.generics import ListAPIView

from .models import Event, EventDate
from .serializers import EventSerializer
from .services import check_date


class EventListView(ListAPIView):
    """
    GET Events
    """
    serializer_class = EventSerializer
    permission_classes = ()

    def dispatch(self, request, *args, **kwargs):
        self.start_date = check_date(request.GET.get('start_date'))
        self.end_date = check_date(request.GET.get('end_date'))
        return super(EventListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        event_dates = EventDate.objects.filter(active=True)

        if self.start_date:
            event_dates = event_dates.filter(
                sale_start_date__date__gte=self.start_date
            )

        if self.end_date:
            event_dates = event_dates.filter(
                sale_end_date__date__lte=self.end_date
            )

        event_dates_ids = [event_date.id for event_date in event_dates]
        return Event.objects.filter(id__in=event_dates_ids, active=True)
