from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name="category_id")
    organizer_id = filters.NumberFilter(field_name="organizer_id")
    date_from = filters.IsoDateTimeFilter(field_name="event_date", lookup_expr="gte")
    date_to = filters.IsoDateTimeFilter(field_name="event_date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["category", "status", "event_type", "organizer_id", "date_from", "date_to"]
