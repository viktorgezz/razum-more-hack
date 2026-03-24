from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APITestCase

from events.models import Event, EventCategory, Participation
from events.services import checkin_for_event, confirm_participation, register_for_event

User = get_user_model()


class EventServicesTests(TestCase):
    """Unit tests for events.services business logic."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="svc_org",
            email="svc_org@test.local",
            password="pass12345",
            role=User.Role.ORGANIZER,
        )
        self.participant = User.objects.create_user(
            username="svc_part",
            email="svc_part@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        self.category = EventCategory.objects.create(name="IT", slug="it", description="")
        self.event = Event.objects.create(
            organizer=self.organizer,
            category=self.category,
            name="Service Test Event",
            description="",
            event_date=timezone.now(),
            event_type=Event.EventType.LECTURE,
            difficulty_coef=Decimal("2.00"),
            base_points=10,
            max_participants=10,
            status=Event.Status.PUBLISHED,
        )

    def test_register_creates_participation(self):
        p, created = register_for_event(self.event, self.participant)
        self.assertTrue(created)
        self.assertEqual(p.status, Participation.Status.REGISTERED)
        self.assertTrue(p.qr_token)

    def test_register_idempotent(self):
        register_for_event(self.event, self.participant)
        p2, created = register_for_event(self.event, self.participant)
        self.assertFalse(created)
        self.assertEqual(p2.status, Participation.Status.REGISTERED)

    def test_register_closed_when_cancelled(self):
        self.event.status = Event.Status.CANCELLED
        self.event.save(update_fields=["status"])
        with self.assertRaises(ValidationError):
            register_for_event(self.event, self.participant)

    def test_register_respects_max_participants(self):
        self.event.max_participants = 1
        self.event.save(update_fields=["max_participants"])
        other = User.objects.create_user(
            username="svc_other",
            email="svc_other@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        register_for_event(self.event, other)
        with self.assertRaises(ValidationError):
            register_for_event(self.event, self.participant)

    def test_register_reopens_after_rejection(self):
        p, _ = register_for_event(self.event, self.participant)
        p.status = Participation.Status.REJECTED
        p.save(update_fields=["status"])
        p2, created = register_for_event(self.event, self.participant)
        self.assertFalse(created)
        self.assertEqual(p2.id, p.id)
        self.assertEqual(p2.status, Participation.Status.REGISTERED)

    def test_checkin_success(self):
        p, _ = register_for_event(self.event, self.participant)
        updated = checkin_for_event(self.event, self.participant, qr_token=p.qr_token)
        self.assertEqual(updated.status, Participation.Status.CHECKED_IN)
        self.assertIsNotNone(updated.checked_in_at)

    def test_checkin_invalid_token(self):
        register_for_event(self.event, self.participant)
        with self.assertRaises(ValidationError):
            checkin_for_event(self.event, self.participant, qr_token="wrong")

    def test_checkin_not_registered(self):
        with self.assertRaises(NotFound):
            checkin_for_event(self.event, self.participant, qr_token="any")

    def test_confirm_from_checked_in(self):
        p, _ = register_for_event(self.event, self.participant)
        checkin_for_event(self.event, self.participant, qr_token=p.qr_token)
        out = confirm_participation(self.event, self.participant)
        self.assertEqual(out.status, Participation.Status.CONFIRMED)
        self.assertEqual(out.points_awarded, self.event.calculate_points())

    def test_confirm_from_registered(self):
        register_for_event(self.event, self.participant)
        out = confirm_participation(self.event, self.participant)
        self.assertEqual(out.status, Participation.Status.CONFIRMED)


class EventsApiTests(APITestCase):
    """Smoke tests for events HTTP API."""

    def setUp(self):
        self.organizer = User.objects.create_user(
            username="api_org",
            email="api_org@test.local",
            password="pass12345",
            role=User.Role.ORGANIZER,
        )
        self.participant = User.objects.create_user(
            username="api_part",
            email="api_part@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        self.category = EventCategory.objects.create(name="Media", slug="media", description="")
        self.event = Event.objects.create(
            organizer=self.organizer,
            category=self.category,
            name="API Event",
            description="",
            event_date=timezone.now(),
            event_type=Event.EventType.LECTURE,
            difficulty_coef=Decimal("1.00"),
            base_points=20,
            status=Event.Status.PUBLISHED,
        )

    def test_list_events_public(self):
        response = self.client.get("/api/v1/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_register_flow(self):
        self.client.force_authenticate(self.participant)
        response = self.client.post(f"/api/v1/events/{self.event.id}/register/", {}, format="json")
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertIn("qr_token", response.data)

        checkin = self.client.post(
            f"/api/v1/events/{self.event.id}/checkin/",
            {"qr_token": response.data["qr_token"]},
            format="json",
        )
        self.assertEqual(checkin.status_code, status.HTTP_200_OK)

    def test_confirm_and_participants_as_organizer(self):
        self.client.force_authenticate(self.participant)
        reg = self.client.post(f"/api/v1/events/{self.event.id}/register/", {}, format="json")
        token = reg.data["qr_token"]
        self.client.post(
            f"/api/v1/events/{self.event.id}/checkin/",
            {"qr_token": token},
            format="json",
        )

        self.client.force_authenticate(self.organizer)
        confirm = self.client.post(
            f"/api/v1/events/{self.event.id}/confirm/{self.participant.id}/",
            {},
            format="json",
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)

        part_list = self.client.get(f"/api/v1/events/{self.event.id}/participants/")
        self.assertEqual(part_list.status_code, status.HTTP_200_OK)
        self.assertIn("results", part_list.data)
        self.assertGreaterEqual(part_list.data.get("count", 0), 1)
