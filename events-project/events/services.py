import secrets

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import Event, Participation


def _is_admin(user) -> bool:
    return getattr(user, "is_superuser", False) or getattr(user, "role", None) == "ADMIN"


def _is_participant(user) -> bool:
    role = getattr(user, "role", None)
    return role in (None, "PARTICIPANT")


def generate_qr_token() -> str:
    return secrets.token_urlsafe(32)


@transaction.atomic
def register_participant(event: Event, user) -> Participation:
    if not _is_participant(user):
        raise PermissionDenied("Only participants can register for events.")

    if event.status not in (Event.Status.PUBLISHED, Event.Status.ONGOING):
        raise DRFValidationError("Registration is available only for published or ongoing events.")

    current_count = Participation.objects.select_for_update().filter(event=event).count()
    if current_count >= event.max_participants:
        raise DRFValidationError("Maximum participants limit reached.")

    try:
        participation = Participation.objects.create(
            event=event,
            user=user,
            qr_token=generate_qr_token(),
        )
    except IntegrityError as exc:
        raise DRFValidationError("User is already registered for this event.") from exc

    return participation


@transaction.atomic
def checkin_participant(event: Event, user, qr_token: str) -> Participation:
    participation = Participation.objects.select_for_update().get(event=event, user=user)

    if participation.qr_token != qr_token:
        raise DRFValidationError("Invalid QR token.")

    if participation.status in (Participation.Status.CONFIRMED, Participation.Status.REJECTED):
        raise DRFValidationError("Participation is already finalized.")

    participation.status = Participation.Status.CHECKED_IN
    participation.checked_in_at = timezone.now()
    participation.save(update_fields=["status", "checked_in_at", "updated_at"])
    return participation


@transaction.atomic
def confirm_participation(event: Event, participant_user, actor) -> Participation:
    is_owner = event.organizer_id == getattr(actor, "id", None)
    if not (is_owner or _is_admin(actor)):
        raise PermissionDenied("Only event organizer or admin can confirm participation.")

    participation = Participation.objects.select_for_update().get(event=event, user=participant_user)

    if participation.status == Participation.Status.CONFIRMED:
        raise DRFValidationError("Participation is already confirmed.")

    if participation.status != Participation.Status.CHECKED_IN:
        raise DRFValidationError("Participant must check in before confirmation.")

    participation.status = Participation.Status.CONFIRMED
    participation.confirmed_at = timezone.now()
    participation.points_awarded = event.base_points
    participation.save(update_fields=["status", "confirmed_at", "points_awarded", "updated_at"])
    return participation
