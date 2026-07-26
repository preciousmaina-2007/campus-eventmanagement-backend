from datetime import date, time

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from .models import Event


class EventCRUDTests(TestCase):
    """Tests for Event CRUD operations and permissions."""

    def setUp(self):
        self.client = APIClient()
        self.organizer = CustomUser.objects.create_user(
            username="organizer", email="organizer@example.com",
            password="StrongPass123!", role="ORGANIZER",
        )
        self.student = CustomUser.objects.create_user(
            username="student", email="student@example.com",
            password="StrongPass123!", role="STUDENT",
        )
        self.admin = CustomUser.objects.create_user(
            username="admin", email="admin@example.com",
            password="StrongPass123!", role="ADMIN",
        )
        self.other_organizer = CustomUser.objects.create_user(
            username="other_organizer", email="other@example.com",
            password="StrongPass123!", role="ORGANIZER",
        )
        self.event_data = {
            "title": "Test Conference", "description": "A test conference event",
            "category": "CONFERENCE", "venue": "Main Hall",
            "event_date": "2026-12-15", "start_time": "09:00:00",
            "end_time": "17:00:00", "capacity": 100,
        }
        self.event = Event.objects.create(
            title="Existing Event", description="An existing event",
            category="WORKSHOP", venue="Room 101",
            event_date=date(2026, 12, 20), start_time=time(10, 0),
            end_time=time(15, 0), capacity=50, organizer=self.organizer,
        )
        self.events_url = "/api/events/"

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.get_token(user)}")

    def test_list_events_authenticated(self):
        self.authenticate(self.student)
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_list_events_unauthenticated(self):
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_event_as_organizer(self):
        self.authenticate(self.organizer)
        response = self.client.post(self.events_url, self.event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], self.event_data["title"])
        self.assertEqual(response.data["organizer_name"], self.organizer.username)
        self.assertEqual(response.data["remaining_slots"], self.event_data["capacity"])

    def test_create_event_as_admin(self):
        self.authenticate(self.admin)
        response = self.client.post(self.events_url, self.event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["organizer_name"], self.admin.username)

    def test_create_event_as_student(self):
        self.authenticate(self.student)
        response = self.client.post(self.events_url, self.event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_event_missing_fields(self):
        self.authenticate(self.organizer)
        response = self.client.post(self.events_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event_invalid_time(self):
        self.authenticate(self.organizer)
        data = {**self.event_data, "start_time": "17:00:00", "end_time": "09:00:00"}
        response = self.client.post(self.events_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_event(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Existing Event")
        self.assertEqual(response.data["organizer_name"], self.organizer.username)

    def test_retrieve_nonexistent_event(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_event_as_owner(self):
        self.authenticate(self.organizer)
        response = self.client.patch(
            f"{self.events_url}{self.event.id}/",
            {"title": "Updated Event Title", "venue": "New Venue"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Event Title")

    def test_update_event_as_admin(self):
        self.authenticate(self.admin)
        response = self.client.patch(
            f"{self.events_url}{self.event.id}/",
            {"title": "Admin Updated Title"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Admin Updated Title")

    def test_update_event_as_non_owner_organizer(self):
        self.authenticate(self.other_organizer)
        response = self.client.patch(
            f"{self.events_url}{self.event.id}/",
            {"title": "Hacked Title"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event_as_student(self):
        self.authenticate(self.student)
        response = self.client.patch(
            f"{self.events_url}{self.event.id}/",
            {"title": "Student Update"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_update_event(self):
        self.authenticate(self.organizer)
        data = {
            "title": "Fully Updated Event", "description": "Updated description",
            "category": "SEMINAR", "venue": "Auditorium",
            "event_date": "2026-12-25", "start_time": "10:00:00",
            "end_time": "12:00:00", "capacity": 200,
        }
        response = self.client.put(f"{self.events_url}{self.event.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Fully Updated Event")
        self.assertEqual(response.data["capacity"], 200)

    def test_delete_event_as_owner(self):
        self.authenticate(self.organizer)
        response = self.client.delete(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_delete_event_as_admin(self):
        self.authenticate(self.admin)
        response = self.client.delete(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_event_as_non_owner(self):
        self.authenticate(self.other_organizer)
        response = self.client.delete(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_as_student(self):
        self.authenticate(self.student)
        response = self.client.delete(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_events(self):
        self.authenticate(self.organizer)
        Event.objects.create(
            title="Second Event", description="Another event", category="SOCIAL",
            venue="Garden", event_date=date(2026, 12, 30),
            start_time=time(14, 0), end_time=time(18, 0), capacity=30,
            organizer=self.organizer,
        )
        response = self.client.get(f"{self.events_url}my_events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_my_events_no_events(self):
        self.authenticate(self.other_organizer)
        response = self.client.get(f"{self.events_url}my_events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_events_by_title(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}?search=Existing")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Existing Event")

    def test_filter_events_by_category(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}?category=WORKSHOP")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_events_by_date(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}?event_date=2026-12-20")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_events_by_date_range(self):
        self.authenticate(self.student)
        Event.objects.create(
            title="Earlier Event", description="Earlier", category="OTHER",
            venue="Room 1", event_date=date(2026, 12, 10),
            start_time=time(9, 0), end_time=time(12, 0), capacity=20, organizer=self.organizer,
        )
        Event.objects.create(
            title="Later Event", description="Later", category="OTHER",
            venue="Room 2", event_date=date(2027, 1, 5),
            start_time=time(9, 0), end_time=time(12, 0), capacity=20, organizer=self.organizer,
        )
        response = self.client.get(
            f"{self.events_url}?event_date__gte=2026-12-15&event_date__lte=2026-12-25"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for event_data in response.data["results"]:
            ev_date = date.fromisoformat(event_data["event_date"])
            self.assertTrue(date(2026, 12, 15) <= ev_date <= date(2026, 12, 25))

    def test_order_events_by_title(self):
        self.authenticate(self.student)
        Event.objects.create(
            title="Alpha Event", description="First", category="OTHER",
            venue="Room A", event_date=date(2026, 12, 10),
            start_time=time(9, 0), end_time=time(12, 0), capacity=20, organizer=self.organizer,
        )
        response = self.client.get(f"{self.events_url}?ordering=title")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [e["title"] for e in response.data["results"]]
        self.assertEqual(titles, sorted(titles))

    def test_order_events_by_event_date(self):
        self.authenticate(self.student)
        response = self.client.get(f"{self.events_url}?ordering=event_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [date.fromisoformat(e["event_date"]) for e in response.data["results"]]
        self.assertEqual(dates, sorted(dates))

    def test_events_pagination(self):
        self.authenticate(self.student)
        for i in range(5):
            Event.objects.create(
                title=f"Paginated Event {i}", description=f"Event {i}", category="OTHER",
                venue="Room P", event_date=date(2026, 12, 10 + i),
                start_time=time(9, 0), end_time=time(12, 0), capacity=20, organizer=self.organizer,
            )
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 6)

    def test_remaining_slots_equals_capacity_on_create(self):
        self.authenticate(self.organizer)
        response = self.client.post(self.events_url, self.event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["remaining_slots"], self.event_data["capacity"])

    def test_unauthenticated_user_cannot_create(self):
        response = self.client.post(self.events_url, self.event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_update(self):
        response = self.client.patch(
            f"{self.events_url}{self.event.id}/",
            {"title": "Unauthorized"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete(self):
        response = self.client.delete(f"{self.events_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
