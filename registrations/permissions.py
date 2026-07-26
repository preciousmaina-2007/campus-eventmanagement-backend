from accounts.permissions import IsOwnerOrAdmin


class IsStudentOrAdmin(IsOwnerOrAdmin):
    """
    Custom permission (extends IsOwnerOrAdmin):
    - Students can create (register) and view their own registrations.
    - Admins can view all registrations and manage them.
    - Organizers cannot register, but can view registrations for their events (list only).
    """

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

