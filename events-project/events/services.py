import secrets

from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from events.models import Event, Participation


def generate_qr_token() -> str:
    return secrets.token_urlsafe(24)


@transaction.atomic
def register_for_event(event: Event, user):
    if event.status in (Event.Status.CANCELLED, Event.Status.COMPLETED):
        raise exceptions.ValidationError("Registration is closed for this event.")

    if event.max_participants:
        current_count = event.participations.exclude(
            status=Participation.Status.REJECTED
        ).count()
        if current_count >= event.max_participants:
            raise exceptions.ValidationError("No slots left for this event.")

    participation, created = Participation.objects.get_or_create(
        event=event,
        user=user,
        defaults={"qr_token": generate_qr_token()},
    )
    if not created and participation.status == Participation.Status.REJECTED:
        participation.status = Participation.Status.REGISTERED
        participation.qr_token = generate_qr_token()
        participation.checked_in_at = None
        participation.confirmed_at = None
        participation.points_awarded = 0
        participation.save(
            update_fields=[
                "status",
                "qr_token",
                "checked_in_at",
                "confirmed_at",
                "points_awarded",
            ]
        )

    return participation, created


@transaction.atomic
def checkin_for_event(event: Event, user, qr_token: str) -> Participation:
    try:
        participation = Participation.objects.select_for_update().get(event=event, user=user)
    except Participation.DoesNotExist as exc:
        raise exceptions.NotFound("You are not registered for this event.") from exc

    if participation.qr_token != qr_token:
        raise exceptions.ValidationError("Invalid QR token.")

    if participation.status in (Participation.Status.CONFIRMED, Participation.Status.REJECTED):
        raise exceptions.ValidationError("Participation cannot be checked in.")

    participation.status = Participation.Status.CHECKED_IN
    participation.checked_in_at = timezone.now()
    participation.save(update_fields=["status", "checked_in_at"])
    return participation


@transaction.atomic
def confirm_participation(event: Event, user) -> Participation:
    try:
        participation = Participation.objects.select_for_update().get(event=event, user=user)
    except Participation.DoesNotExist as exc:
        raise exceptions.NotFound("Participation not found.") from exc

    if participation.status not in (Participation.Status.CHECKED_IN, Participation.Status.REGISTERED):
        raise exceptions.ValidationError("Only registered/checked-in users can be confirmed.")

    participation.status = Participation.Status.CONFIRMED
    participation.confirmed_at = timezone.now()
    participation.points_awarded = event.calculate_points()
    participation.save(update_fields=["status", "confirmed_at", "points_awarded"])
    return participation
