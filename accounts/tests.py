from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .permissions import (
    IsAdmin,
    IsOrganizer,
    IsOrganizerOrReadOnly,
    IsOwnerOrAdmin,
    IsStudent,
)


class RegistrationTests(TestCase):
    """Tests for user registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"

    def test_user_registration(self):
        """Test successful user registration with valid data."""
        data = {
            "username": "teststudent",
            "email": "student@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "role": "STUDENT",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["user"]["username"], "teststudent")
        self.assertEqual(response.data["user"]["role"], "STUDENT")
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_registration_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "StrongPass123!",
            "password2": "DifferentPass456!",
            "role": "STUDENT",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_no_role_defaults_to_student(self):
        """Test that when no role is provided, user defaults to STUDENT."""
        data = {
            "username": "teststudent2",
            "email": "student2@example.com",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["role"], "STUDENT")

    def test_registration_missing_fields(self):
        """Test registration fails when required fields are missing."""
        data = {"username": "testuser"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_weak_password(self):
        """Test registration fails with a weak/common password."""
        data = {
            "username": "testuser",
            "email": "user@example.com",
            "password": "password123",
            "password2": "password123",
            "role": "STUDENT",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """Tests for JWT login endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = "/api/auth/login/"
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123!",
            role="STUDENT",
        )

    def test_login_success(self):
        """Test successful login returns access and refresh tokens."""
        data = {"username": "testuser", "password": "StrongPass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login fails with wrong password."""
        data = {"username": "testuser", "password": "WrongPass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login fails for a user that doesn't exist."""
        data = {"username": "nouser", "password": "StrongPass123!"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(TestCase):
    """Tests for JWT token refresh endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.refresh_url = "/api/auth/refresh/"
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123!",
            role="STUDENT",
        )

    def test_token_refresh(self):
        """Test that a valid refresh token returns a new access token."""
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh": str(refresh)}
        response = self.client.post(self.refresh_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid(self):
        """Test that an invalid refresh token is rejected."""
        data = {"refresh": "invalidtoken123"}
        response = self.client.post(self.refresh_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(TestCase):
    """Tests for user profile retrieval and update."""

    def setUp(self):
        self.client = APIClient()
        self.profile_url = "/api/auth/profile/"
        self.update_url = "/api/auth/profile/update/"
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123!",
            role="STUDENT",
        )
        # Obtain JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_profile_retrieval(self):
        """Test authenticated user can retrieve their profile."""
        self.authenticate()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["role"], "STUDENT")

    def test_profile_unauthenticated(self):
        """Test unauthenticated request to profile returns 401."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update(self):
        """Test authenticated user can update their profile."""
        self.authenticate()
        data = {"username": "newusername", "email": "newemail@example.com"}
        response = self.client.put(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["user"]["username"], "newusername")
        # Verify DB was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")

    def test_profile_partial_update(self):
        """Test PATCH works for partial profile update."""
        self.authenticate()
        data = {"username": "partialupdate"}
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "partialupdate")
        # Email should remain unchanged
        self.assertEqual(self.user.email, "test@example.com")

    def test_profile_update_unauthenticated(self):
        """Test unauthenticated user cannot update profile."""
        data = {"username": "newusername"}
        response = self.client.put(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionUnitTests(TestCase):
    """Unit tests for custom permission classes."""

    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username="student",
            password="pass123",
            role="STUDENT",
        )
        self.organizer = CustomUser.objects.create_user(
            username="organizer",
            password="pass123",
            role="ORGANIZER",
        )
        self.admin = CustomUser.objects.create_user(
            username="admin",
            password="pass123",
            role="ADMIN",
        )
        # Mock request and view
        self.mock_request = type("Request", (), {"user": None})()
        self.mock_view = type("View", (), {})()

    def test_is_student_permission(self):
        """Test IsStudent permission grants access only to STUDENT role."""
        permission = IsStudent()

        # Student should have access
        self.mock_request.user = self.student
        self.assertTrue(permission.has_permission(self.mock_request, self.mock_view))

        # Organizer should not
        self.mock_request.user = self.organizer
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

        # Admin should not
        self.mock_request.user = self.admin
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

    def test_is_organizer_permission(self):
        """Test IsOrganizer permission grants access only to ORGANIZER role."""
        permission = IsOrganizer()

        self.mock_request.user = self.organizer
        self.assertTrue(permission.has_permission(self.mock_request, self.mock_view))

        self.mock_request.user = self.student
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

        self.mock_request.user = self.admin
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

    def test_is_admin_permission(self):
        """Test IsAdmin permission grants access only to ADMIN role."""
        permission = IsAdmin()

        self.mock_request.user = self.admin
        self.assertTrue(permission.has_permission(self.mock_request, self.mock_view))

        self.mock_request.user = self.student
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

        self.mock_request.user = self.organizer
        self.assertFalse(permission.has_permission(self.mock_request, self.mock_view))

    def test_is_organizer_or_read_only_safe_methods(self):
        """Test IsOrganizerOrReadOnly allows any authenticated user safe methods."""
        permission = IsOrganizerOrReadOnly()

        # Safe methods should be allowed for all authenticated users
        for method in ["GET", "HEAD", "OPTIONS"]:
            self.mock_request.method = method
            self.mock_request.user = self.student
            self.assertTrue(
                permission.has_permission(self.mock_request, self.mock_view)
            )

            self.mock_request.user = self.organizer
            self.assertTrue(
                permission.has_permission(self.mock_request, self.mock_view)
            )

    def test_is_organizer_or_read_only_unsafe_methods(self):
        """Test IsOrganizerOrReadOnly blocks non-organizer unsafe methods."""
        permission = IsOrganizerOrReadOnly()

        # Unsafe methods blocked for students
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.mock_request.method = method
            self.mock_request.user = self.student
            self.assertFalse(
                permission.has_permission(self.mock_request, self.mock_view)
            )

        # Unsafe methods allowed for organizer
        self.mock_request.user = self.organizer
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.mock_request.method = method
            self.assertTrue(
                permission.has_permission(self.mock_request, self.mock_view)
            )

        # Unsafe methods allowed for admin
        self.mock_request.user = self.admin
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.mock_request.method = method
            self.assertTrue(
                permission.has_permission(self.mock_request, self.mock_view)
            )

    def test_is_organizer_or_read_only_object_permission(self):
        """Test object-level permission for IsOrganizerOrReadOnly."""
        permission = IsOrganizerOrReadOnly()

        # Mock an object with an organizer field
        class MockEvent:
            def __init__(self, organizer):
                self.organizer = organizer

        event = MockEvent(self.organizer)

        # Admin can do anything
        self.mock_request.user = self.admin
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            self.mock_request.method = method
            self.assertTrue(
                permission.has_object_permission(
                    self.mock_request, self.mock_view, event
                )
            )

        # Organizer can modify own event
        self.mock_request.user = self.organizer
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.mock_request.method = method
            self.assertTrue(
                permission.has_object_permission(
                    self.mock_request, self.mock_view, event
                )
            )

        # Different organizer cannot modify
        other_organizer = CustomUser.objects.create_user(
            username="other_org", password="pass123", role="ORGANIZER"
        )
        self.mock_request.user = other_organizer
        self.mock_request.method = "PUT"
        self.assertFalse(
            permission.has_object_permission(
                self.mock_request, self.mock_view, event
            )
        )

    def test_is_owner_or_admin(self):
        """Test IsOwnerOrAdmin permission logic."""
        permission = IsOwnerOrAdmin()

        class MockRegistration:
            def __init__(self, student):
                self.student = student

        registration = MockRegistration(self.student)

        # Admin can do anything
        self.mock_request.user = self.admin
        self.mock_request.method = "DELETE"
        self.assertTrue(
            permission.has_permission(self.mock_request, self.mock_view)
        )
        self.assertTrue(
            permission.has_object_permission(
                self.mock_request, self.mock_view, registration
            )
        )

        # Owner can modify own registration
        self.mock_request.user = self.student
        self.mock_request.method = "PUT"
        self.assertTrue(
            permission.has_object_permission(
                self.mock_request, self.mock_view, registration
            )
        )

        # Non-owner student cannot modify
        other_student = CustomUser.objects.create_user(
            username="other_student", password="pass123", role="STUDENT"
        )
        self.mock_request.user = other_student
        self.assertFalse(
            permission.has_object_permission(
                self.mock_request, self.mock_view, registration
            )
        )
