from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "event",
        "status",
        "registered_at",
    ]
    list_filter = ["status", "event", "registered_at"]
    search_fields = ["student__username", "event__title"]
    date_hierarchy = "registered_at"
    readonly_fields = ["registered_at"]

