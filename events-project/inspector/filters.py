from django.db.models import QuerySet


ALLOWED_ORDERING = {
    "total_points": "total_points",
    "-total_points": "-total_points",
    "avg_points": "avg_points",
    "-avg_points": "-avg_points",
    "events_count": "events_count",
    "-events_count": "-events_count",
    "date_joined": "date_joined",
    "-date_joined": "-date_joined",
}


def apply_candidate_filters(queryset: QuerySet, params) -> QuerySet:
    min_events = params.get("min_events")
    max_events = params.get("max_events")
    min_avg_points = params.get("min_avg_points")
    max_avg_points = params.get("max_avg_points")
    ordering = params.get("ordering", "-total_points")

    if min_events is not None:
        queryset = queryset.filter(events_count__gte=min_events)
    if max_events is not None:
        queryset = queryset.filter(events_count__lte=max_events)
    if min_avg_points is not None:
        queryset = queryset.filter(avg_points__gte=min_avg_points)
    if max_avg_points is not None:
        queryset = queryset.filter(avg_points__lte=max_avg_points)

    queryset = queryset.order_by(ALLOWED_ORDERING.get(ordering, "-total_points"))
    return queryset
