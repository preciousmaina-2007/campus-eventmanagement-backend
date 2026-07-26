from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow users with STUDENT role.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "STUDENT"
        )


class IsOrganizer(permissions.BasePermission):
    """
    Custom permission to only allow users with ORGANIZER role.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ORGANIZER"
        )


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users with ADMIN role.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - SAFE_METHODS (GET, HEAD, OPTIONS) allowed for any authenticated user.
    - Only ORGANIZER and ADMIN roles can create, update, or delete.
    - For unsafe methods on existing objects, only the organizer who owns the object
      or admin can proceed (checked via has_object_permission).
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Read-only for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations require ORGANIZER or ADMIN role
        return request.user.role in ["ORGANIZER", "ADMIN"]

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == "ADMIN":
            return True

        # Read-only for any (authenticated) user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Organizers can only modify their own objects
        # Assumes obj has an `organizer` field pointing to the user
        return getattr(obj, "organizer", None) == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Admin has full access.
    - Object owners have full access to their own objects.
    - Others have read-only access.
    - For list views, only admins see all objects; owners see filtered querysets.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == "ADMIN":
            return True

        # Read-only for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Owner has full access; assumes obj has a `student` or `user` field
        owner = getattr(obj, "student", None) or getattr(obj, "user", None)
        return owner == request.user

