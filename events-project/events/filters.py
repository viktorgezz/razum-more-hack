from django.db.models import QuerySet

from events.models import Event


def filter_events(queryset: QuerySet[Event], params) -> QuerySet[Event]:
    category_slug = params.get("category")
    status_value = params.get("status")
    event_type = params.get("event_type")
    organizer_id = params.get("organizer_id")
    date_from = params.get("date_from")
    date_to = params.get("date_to")

    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    if status_value:
        queryset = queryset.filter(status=status_value)
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    if organizer_id:
        queryset = queryset.filter(organizer_id=organizer_id)
    if date_from:
        queryset = queryset.filter(event_date__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(event_date__date__lte=date_to)

    return queryset
