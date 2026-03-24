from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from events.models import Event, EventCategory, Participation

User = get_user_model()


class InspectorApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            username="inspector_admin",
            email="inspector_admin@test.local",
            password="testpass123",
            role=User.Role.OBSERVER,
        )
        cls.regular = User.objects.create_user(
            username="regular_user",
            email="regular@test.local",
            password="testpass123",
            role=User.Role.PARTICIPANT,
        )
        cls.candidate = User.objects.create_user(
            username="candidate_1",
            email="candidate_1@test.local",
            password="testpass123",
            role=User.Role.PARTICIPANT,
        )
        organizer = User.objects.create_user(
            username="organizer_for_inspector",
            email="org@test.local",
            password="testpass123",
            role=User.Role.ORGANIZER,
        )
        category = EventCategory.objects.create(name="IT", slug="it", description="IT events")
        event = Event.objects.create(
            organizer=organizer,
            category=category,
            name="Inspector Test Event",
            description="desc",
            event_date=timezone.now() - timedelta(days=2),
            event_type=Event.EventType.LECTURE,
            difficulty_coef=Decimal("1.50"),
            base_points=30,
            max_participants=20,
            status=Event.Status.COMPLETED,
        )
        Participation.objects.create(
            event=event,
            user=cls.candidate,
            status=Participation.Status.CONFIRMED,
            qr_token="token-inspector-1",
            checked_in_at=timezone.now() - timedelta(days=1),
            confirmed_at=timezone.now(),
            points_awarded=45,
        )

    def test_inspector_requires_authentication(self):
        response = self.client.get("/api/inspector/candidates/")
        self.assertEqual(response.status_code, 401)

    def test_inspector_denies_non_observer(self):
        self.client.force_authenticate(self.regular)
        response = self.client.get("/api/inspector/candidates/")
        self.assertEqual(response.status_code, 403)

    def test_candidates_filters_and_response(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get("/api/inspector/candidates/?min_events=1&ordering=-total_points")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertGreaterEqual(len(response.data["results"]), 1)
        first = response.data["results"][0]
        self.assertIn("events_count", first)
        self.assertIn("total_points", first)

    def test_candidate_report_pdf(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(f"/api/inspector/candidates/{self.candidate.id}/report/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
