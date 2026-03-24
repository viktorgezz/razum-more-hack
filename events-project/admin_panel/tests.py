from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from events.models import EventCategory
from rating.models import PointWeight

User = get_user_model()


class AdminPanelApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user(
            username="panel_admin",
            password="testpass123",
            email="panel_admin@test.local",
            is_staff=True,
        )
        cls.regular_user = User.objects.create_user(
            username="panel_regular",
            password="testpass123",
            email="panel_regular@test.local",
        )
        cls.pending_user = User.objects.create_user(
            username="pending_organizer",
            password="testpass123",
            email="pending_organizer@test.local",
            is_staff=False,
        )
        cls.category = EventCategory.objects.create(name="IT", slug="it", description="IT")
        cls.weight = PointWeight.objects.create(
            event_type="LECTURE",
            category=cls.category,
            weight=Decimal("1.50"),
            updated_by=cls.admin_user,
        )

    def test_requires_authentication(self):
        response = self.client.get("/api/admin/organizers/pending/")
        self.assertEqual(response.status_code, 401)

    def test_denies_non_staff(self):
        self.client.force_authenticate(self.regular_user)
        response = self.client.get("/api/admin/organizers/pending/")
        self.assertEqual(response.status_code, 403)

    def test_pending_organizers_list(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get("/api/admin/organizers/pending/")
        self.assertEqual(response.status_code, 200)
        usernames = [item["username"] for item in response.data["results"]]
        self.assertIn("pending_organizer", usernames)
        self.assertIn("panel_regular", usernames)
        self.assertNotIn("panel_admin", usernames)

    def test_approve_and_reject_organizer(self):
        self.client.force_authenticate(self.admin_user)
        approve_response = self.client.post(f"/api/admin/organizers/{self.pending_user.id}/approve/")
        self.assertEqual(approve_response.status_code, 200)
        self.pending_user.refresh_from_db()
        self.assertTrue(self.pending_user.is_staff)
        self.assertEqual(self.pending_user.role, User.Role.ORGANIZER)

        reject_response = self.client.post(f"/api/admin/organizers/{self.pending_user.id}/reject/")
        self.assertEqual(reject_response.status_code, 200)
        self.pending_user.refresh_from_db()
        self.assertFalse(self.pending_user.is_staff)
        self.assertEqual(self.pending_user.role, User.Role.PARTICIPANT)

    def test_point_weights_list_and_patch(self):
        self.client.force_authenticate(self.admin_user)
        list_response = self.client.get("/api/admin/point-weights/")
        self.assertEqual(list_response.status_code, 200)
        self.assertIn("results", list_response.data)

        patch_response = self.client.patch(
            f"/api/admin/point-weights/{self.weight.id}/",
            data={"weight": "2.25"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.weight.refresh_from_db()
        self.assertEqual(self.weight.weight, Decimal("2.25"))
        self.assertEqual(self.weight.updated_by_id, self.admin_user.id)

    def test_point_weight_validation(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.patch(
            f"/api/admin/point-weights/{self.weight.id}/",
            data={"weight": "0"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
