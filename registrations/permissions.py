from rest_framework import permissions


class IsStudentOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Students can create (register) and view their own registrations.
    - Admins can view all registrations and manage them.
    - Organizers cannot register, but can view registrations for their events (list only).
    """

    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == "ADMIN":
            return True

        # Students can only access their own registrations
        if request.user.role == "STUDENT":
            return obj.student == request.user

        # Organizers can access registrations for their events
        if request.user.role == "ORGANIZER":
            return obj.event.organizer == request.user

        return False

