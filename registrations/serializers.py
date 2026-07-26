from rest_framework import serializers

from events.models import Event
from events.serializers import EventSerializer

from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    event_details = EventSerializer(source="event", read_only=True)

    class Meta:
        model = Registration
        fields = [
            "id",
            "student",
            "student_name",
            "event",
            "event_details",
            "status",
            "registered_at",
        ]
        read_only_fields = [
            "id",
            "student",
            "student_name",
            "event_details",
            "registered_at",
        ]

    def get_student_name(self, obj):
        return obj.student.username


class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["event"]

    def validate_event(self, value):
        request = self.context.get("request")
        user = request.user

        # Check if user is an organizer (cannot register)
        if user.role == "ORGANIZER":
            raise serializers.ValidationError(
                "Organizers cannot register for events."
            )

        # Check if user is the organizer of this event
        if value.organizer == user:
            raise serializers.ValidationError(
                "You cannot register for your own event."
            )

        # Check if user already registered
        if Registration.objects.filter(student=user, event=value).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )

        # Check if event is full
        if value.remaining_slots <= 0:
            raise serializers.ValidationError(
                "This event is fully booked. No slots available."
            )

        return value

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["student"] = request.user
        validated_data["status"] = Registration.Status.REGISTERED
        return super().create(validated_data)

