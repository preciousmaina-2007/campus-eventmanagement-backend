from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "category",
            "venue",
            "event_date",
            "start_time",
            "end_time",
            "capacity",
            "remaining_slots",
            "image",
            "organizer",
            "organizer_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organizer",
            "organizer_name",
            "remaining_slots",
            "created_at",
            "updated_at",
        ]

    def get_organizer_name(self, obj):
        return obj.organizer.username

    def validate_remaining_slots(self, value):
        if self.instance and value > self.instance.capacity:
            raise serializers.ValidationError(
                "Remaining slots cannot exceed capacity."
            )
        return value


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "venue",
            "event_date",
            "start_time",
            "end_time",
            "capacity",
            "image",
        ]

    def validate(self, data):
        if data.get("start_time") and data.get("end_time"):
            if data["start_time"] >= data["end_time"]:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )
        return data

