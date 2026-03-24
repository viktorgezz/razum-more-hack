from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from events.models import Event, EventCategory, Participation
from organizers.models import OrganizerReview

User = get_user_model()


class OrganizersApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.organizer = User.objects.create_user(
            username="org_prof",
            email="org_prof@test.local",
            password="pass12345",
            role=User.Role.ORGANIZER,
        )
        cls.participant = User.objects.create_user(
            username="org_part",
            email="org_part@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        cls.other = User.objects.create_user(
            username="org_other",
            email="org_other@test.local",
            password="pass12345",
            role=User.Role.PARTICIPANT,
        )
        cls.category = EventCategory.objects.create(name="IT", slug="it", description="")
        cls.event = Event.objects.create(
            organizer=cls.organizer,
            category=cls.category,
            name="Org Test Event",
            description="",
            event_date=timezone.now(),
            event_type=Event.EventType.LECTURE,
            difficulty_coef=Decimal("1.00"),
            base_points=10,
            status=Event.Status.COMPLETED,
        )
        Participation.objects.create(
            event=cls.event,
            user=cls.participant,
            status=Participation.Status.CONFIRMED,
            qr_token="org-tok-1",
            points_awarded=10,
        )

    def test_list_requires_auth(self):
        response = self.client.get("/api/v1/organizers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_and_profile(self):
        self.client.force_authenticate(self.other)
        lst = self.client.get("/api/v1/organizers/")
        self.assertEqual(lst.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in lst.data["results"]]
        self.assertIn(self.organizer.id, ids)

        prof = self.client.get(f"/api/v1/organizers/{self.organizer.id}/")
        self.assertEqual(prof.status_code, status.HTTP_200_OK)
        self.assertEqual(prof.data["username"], self.organizer.username)
        self.assertIn("events_count", prof.data)

    def test_organizer_events(self):
        self.client.force_authenticate(self.other)
        response = self.client.get(f"/api/v1/organizers/{self.organizer.id}/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_create_review_as_participant(self):
        self.client.force_authenticate(self.participant)
        response = self.client.post(
            f"/api/v1/organizers/{self.organizer.id}/reviews/create/",
            {"event": self.event.id, "score": 5, "comment": "ok"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrganizerReview.objects.filter(reviewer=self.participant).count(), 1)

    def test_cannot_review_twice(self):
        self.client.force_authenticate(self.participant)
        self.client.post(
            f"/api/v1/organizers/{self.organizer.id}/reviews/create/",
            {"event": self.event.id, "score": 4, "comment": "first"},
            format="json",
        )
        response = self.client.post(
            f"/api/v1/organizers/{self.organizer.id}/reviews/create/",
            {"event": self.event.id, "score": 3, "comment": "second"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_own_review(self):
        self.client.force_authenticate(self.participant)
        created = self.client.post(
            f"/api/v1/organizers/{self.organizer.id}/reviews/create/",
            {"event": self.event.id, "score": 5, "comment": "del"},
            format="json",
        )
        review_id = created.data["id"]
        response = self.client.delete(
            f"/api/v1/organizers/{self.organizer.id}/reviews/{review_id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
