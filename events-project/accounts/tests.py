from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.permissions import IsAdmin, IsObserver, IsOrganizer, IsParticipant

User = get_user_model()


class AccountsApiTests(APITestCase):
    def test_register_success(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "new_user",
                "email": "new_user@test.local",
                "password": "StrongPass123!",
                "first_name": "New",
                "last_name": "User",
                "role": "PARTICIPANT",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "new_user")
        self.assertNotIn("password", response.data)

    def test_register_validation_error(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {"username": "bad_user", "password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        user = User.objects.create_user(
            username="login_user",
            email="login_user@test.local",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        User.objects.create_user(
            username="invalid_user",
            email="invalid_user@test.local",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "invalid_user", "password": "WrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_token(self):
        user = User.objects.create_user(
            username="refresh_user",
            email="refresh_user@test.local",
            password="StrongPass123!",
        )
        refresh = str(RefreshToken.for_user(user))
        response = self.client.post(
            "/api/v1/auth/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_me_requires_auth(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_me_with_jwt(self):
        user = User.objects.create_user(
            username="me_user",
            email="me_user@test.local",
            password="StrongPass123!",
        )
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "me_user")


class AccountsPermissionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.organizer = User.objects.create_user(username="org", password="StrongPass123!", role="ORGANIZER")
        self.participant = User.objects.create_user(
            username="participant", password="StrongPass123!", role="PARTICIPANT"
        )
        self.observer = User.objects.create_user(username="observer", password="StrongPass123!", role="OBSERVER")
        self.admin_role = User.objects.create_user(username="admin_role", password="StrongPass123!", role="ADMIN")

    def _request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def test_role_permissions(self):
        self.assertTrue(IsOrganizer().has_permission(self._request(self.organizer), None))
        self.assertTrue(IsParticipant().has_permission(self._request(self.participant), None))
        self.assertTrue(IsObserver().has_permission(self._request(self.observer), None))
        self.assertTrue(IsAdmin().has_permission(self._request(self.admin_role), None))
        self.assertFalse(IsOrganizer().has_permission(self._request(self.participant), None))
