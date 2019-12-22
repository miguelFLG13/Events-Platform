from rest_framework.serializers import ModelSerializer

from .models import Event


class EventSerializer(ModelSerializer):

    class Meta:
        model = Event
        fields = ('uuid', 'title', )
        read_only_fields = ('uuid', 'title', )
