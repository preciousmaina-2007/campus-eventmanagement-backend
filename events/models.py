from django.conf import settings
from django.db import models


class Event(models.Model):
    class Category(models.TextChoices):
        CONFERENCE = "CONFERENCE", "Conference"
        WORKSHOP = "WORKSHOP", "Workshop"
        SEMINAR = "SEMINAR", "Seminar"
        SOCIAL = "SOCIAL", "Social"
        SPORTS = "SPORTS", "Sports"
        CULTURAL = "CULTURAL", "Cultural"
        OTHER = "OTHER", "Other"

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    venue = models.CharField(max_length=200)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    remaining_slots = models.PositiveIntegerField()
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Set remaining_slots to capacity on creation
        if not self.pk:
            self.remaining_slots = self.capacity
        super().save(*args, **kwargs)

