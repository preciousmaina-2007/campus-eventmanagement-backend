from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "venue",
        "event_date",
        "start_time",
        "end_time",
        "capacity",
        "remaining_slots",
        "organizer",
        "created_at",
    ]
    list_filter = ["category", "event_date", "organizer"]
    search_fields = ["title", "description", "venue"]
    date_hierarchy = "event_date"

