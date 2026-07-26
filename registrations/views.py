from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsOwnerOrAdmin
from .models import Registration
from .permissions import IsStudentOrAdmin
from .serializers import RegistrationCreateSerializer, RegistrationSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStudentOrAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return RegistrationCreateSerializer
        return RegistrationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN":
            return Registration.objects.all()
        elif user.role == "ORGANIZER":
            # Organizers see registrations for their events
            return Registration.objects.filter(event__organizer=user)
        # Students see only their own registrations
        return Registration.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        # When a registration is deleted, restore the slot
        if instance.status == Registration.Status.REGISTERED:
            event = instance.event
            event.remaining_slots += 1
            event.save(update_fields=["remaining_slots"])
        instance.delete()

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        """Cancel a registration."""
        registration = self.get_object()

        if registration.status != Registration.Status.REGISTERED:
            return Response(
                {"detail": "Only active registrations can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore slot
        event = registration.event
        event.remaining_slots += 1
        event.save(update_fields=["remaining_slots"])

        registration.status = Registration.Status.CANCELLED
        registration.save(update_fields=["status"])

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def mark_attended(self, request, pk=None):
        """Mark a registration as attended (Admin/Organizer only)."""
        registration = self.get_object()

        if request.user.role not in ["ADMIN", "ORGANIZER"]:
            return Response(
                {"detail": "Only admins and organizers can mark attendance."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if registration.status != Registration.Status.REGISTERED:
            return Response(
                {"detail": "Only active registrations can be marked as attended."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.status = Registration.Status.ATTENDED
        registration.save(update_fields=["status"])

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)

