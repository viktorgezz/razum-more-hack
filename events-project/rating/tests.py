from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event, EventCategory, Participation
from rating.models import PointWeight, RatingSnapshot
from rating.services import (
    calculate_user_rating,
    rebuild_leaderboard,
    update_user_snapshot,
)

User = get_user_model()


class RatingServicesTests(TestCase):
    """Tests for rating.services calculation and leaderboard rebuild."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="r_org",
            email="r_org@test.local",
            password="pass12345",
            role=User.Role.ORGANIZER,
        )
        self.cat_it = EventCategory.objects.create(name="IT", slug="it", description="")
        self.cat_social = EventCategory.objects.create(
            name="Social", slug="social", description=""
        )
        self.participant_a = User.objects.create_user(
            username="r_p_a",
            email="r_p_a@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        self.participant_b = User.objects.create_user(
            username="r_p_b",
            email="r_p_b@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )

    def _make_event(self, category, base_points=10, coef="1.00"):
        return Event.objects.create(
            organizer=self.organizer,
            category=category,
            name="Rating event",
            description="",
            event_date=timezone.now(),
            event_type=Event.EventType.LECTURE,
            difficulty_coef=Decimal(coef),
            base_points=base_points,
            status=Event.Status.COMPLETED,
        )

    def test_calculate_user_rating_empty(self):
        totals = calculate_user_rating(self.participant_a.id)
        self.assertEqual(totals["common_rating"], Decimal("0"))
        self.assertEqual(totals["rating_it"], Decimal("0"))

    def test_calculate_user_rating_with_weight_and_split(self):
        PointWeight.objects.create(
            event_type=Event.EventType.LECTURE,
            category=self.cat_it,
            weight=Decimal("2.0"),
            updated_by=self.organizer,
        )
        PointWeight.objects.create(
            event_type=Event.EventType.LECTURE,
            category=None,
            weight=Decimal("1.0"),
            updated_by=self.organizer,
        )

        ev_it = self._make_event(self.cat_it, base_points=10, coef="1.50")
        ev_soc = self._make_event(self.cat_social, base_points=20, coef="1.00")

        Participation.objects.create(
            event=ev_it,
            user=self.participant_a,
            status=Participation.Status.CONFIRMED,
            qr_token="tok-r-1",
            points_awarded=10,
        )
        Participation.objects.create(
            event=ev_soc,
            user=self.participant_a,
            status=Participation.Status.CONFIRMED,
            qr_token="tok-r-2",
            points_awarded=20,
        )

        totals = calculate_user_rating(self.participant_a.id)
        # IT: 10 * 1.5 * 2.0 = 30
        self.assertEqual(totals["rating_it"], Decimal("30"))
        # Social: 20 * 1.0 * 1.0 (fallback) -> rating_social
        self.assertEqual(totals["rating_social"], Decimal("20"))
        self.assertEqual(totals["common_rating"], Decimal("50"))

    def test_update_user_snapshot(self):
        ev = self._make_event(self.cat_it, base_points=5, coef="1.00")
        Participation.objects.create(
            event=ev,
            user=self.participant_a,
            status=Participation.Status.CONFIRMED,
            qr_token="tok-r-3",
            points_awarded=5,
        )
        snap = update_user_snapshot(self.participant_a.id)
        self.assertEqual(snap.user_id, self.participant_a.id)
        self.assertGreaterEqual(snap.common_rating, Decimal("0"))

    def test_rebuild_leaderboard_assigns_ranks(self):
        ev = self._make_event(self.cat_it, base_points=100, coef="1.00")
        Participation.objects.create(
            event=ev,
            user=self.participant_a,
            status=Participation.Status.CONFIRMED,
            qr_token="tok-r-4",
            points_awarded=100,
        )
        Participation.objects.create(
            event=ev,
            user=self.participant_b,
            status=Participation.Status.CONFIRMED,
            qr_token="tok-r-5",
            points_awarded=10,
        )

        rebuild_leaderboard()

        sa = RatingSnapshot.objects.get(user=self.participant_a)
        sb = RatingSnapshot.objects.get(user=self.participant_b)
        self.assertLess(sa.rank, sb.rank)
        self.assertEqual(sa.rank, 1)


class RatingApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rating_api_user",
            email="rating_api@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        self.admin = User.objects.create_user(
            username="rating_admin",
            email="rating_admin@test.local",
            password="pass12345",
            role=User.Role.ADMIN,
        )

    def test_leaderboard_requires_auth(self):
        response = self.client.get("/api/v1/ratings/leaderboard/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_leaderboard_authenticated(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/ratings/leaderboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rebuild_requires_admin(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/api/v1/ratings/rebuild/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/v1/ratings/rebuild/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "ok")
