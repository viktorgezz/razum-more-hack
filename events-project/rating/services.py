from decimal import Decimal

from accounts.models import User
from events.models import Participation
from rating.models import PointWeight, RatingSnapshot


CATEGORY_RATING_MAP = {
    'it': 'rating_it',
    'social': 'rating_social',
    'media': 'rating_media',
}


def _get_weight(event_type, category_slug):
    """Return the PointWeight for the given event_type + category, with fallback."""
    if category_slug:
        try:
            return PointWeight.objects.get(
                event_type=event_type,
                category__slug=category_slug,
            ).weight
        except PointWeight.DoesNotExist:
            pass

    try:
        return PointWeight.objects.get(
            event_type=event_type,
            category=None,
        ).weight
    except PointWeight.DoesNotExist:
        return Decimal('1.0')


def calculate_user_rating(user_id):
    """Calculate rating totals from all CONFIRMED participations."""
    participations = (
        Participation.objects
        .filter(user_id=user_id, status=Participation.Status.CONFIRMED)
        .select_related('event', 'event__category')
    )

    totals = {
        'common_rating': Decimal('0'),
        'rating_it': Decimal('0'),
        'rating_social': Decimal('0'),
        'rating_media': Decimal('0'),
    }

    for p in participations:
        event = p.event
        cat_slug = event.category.slug if event.category else None
        weight = _get_weight(event.event_type, cat_slug)
        points = Decimal(p.points_awarded) * event.difficulty_coef * weight

        totals['common_rating'] += points

        if cat_slug and cat_slug in CATEGORY_RATING_MAP:
            totals[CATEGORY_RATING_MAP[cat_slug]] += points

    return totals


def update_user_snapshot(user_id):
    """Calculate rating and update_or_create the user's RatingSnapshot."""
    totals = calculate_user_rating(user_id)
    snapshot, _ = RatingSnapshot.objects.update_or_create(
        user_id=user_id,
        defaults=totals,
    )
    return snapshot


def rebuild_leaderboard():
    """Recalculate ratings for all PARTICIPANTs and assign ranks."""
    participant_ids = User.objects.filter(
        role=User.Role.PARTICIPANT,
    ).values_list('id', flat=True)

    for uid in participant_ids:
        update_user_snapshot(uid)

    snapshots = list(
        RatingSnapshot.objects
        .filter(user__role=User.Role.PARTICIPANT)
        .order_by('-common_rating')
    )

    for position, snap in enumerate(snapshots, start=1):
        snap.rank = position

    RatingSnapshot.objects.bulk_update(snapshots, ['rank'])
