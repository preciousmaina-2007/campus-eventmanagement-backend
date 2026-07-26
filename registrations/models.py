from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Registration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Registered"
        CANCELLED = "CANCELLED", "Cancelled"
        ATTENDED = "ATTENDED", "Attended"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-registered_at"]
        unique_together = ["student", "event"]
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"

    def __str__(self):
        return f"{self.student.username} -> {self.event.title} ({self.get_status_display()})"

    def clean(self):
        """Validate that the event has available slots and user isn't the organizer."""
        if self.event.remaining_slots <= 0:
            raise ValidationError("Event is full. No remaining slots available.")
        if self.student == self.event.organizer:
            raise ValidationError("The event organizer cannot register for their own event.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.clean()
            # Decrement remaining_slots on new registration
            self.event.remaining_slots -= 1
            self.event.save(update_fields=["remaining_slots"])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Increment remaining_slots when registration is deleted (cancelled)
        if self.status == self.Status.REGISTERED:
            self.event.remaining_slots += 1
            self.event.save(update_fields=["remaining_slots"])
        super().delete(*args, **kwargs)

