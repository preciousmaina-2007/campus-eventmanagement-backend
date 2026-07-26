from rest_framework import permissions


class IsOrganizerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Only organizers can create events (students cannot).
    - Organizers can only edit/delete their own events.
    - Admin has full access.
    """

    def has_permission(self, request, view):
        # Allow authenticated users to list/retrieve
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Only organizers and admins can create
        if request.method == "POST":
            return (
                request.user.is_authenticated
                and request.user.role in ["ORGANIZER", "ADMIN"]
            )

        # For PUT, PATCH, DELETE – check object-level permission
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == "ADMIN":
            return True

        # Organizers can only edit/delete their own events
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.organizer == request.user

