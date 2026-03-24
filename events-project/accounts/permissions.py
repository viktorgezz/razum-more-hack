from rest_framework.permissions import BasePermission


class _RolePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == self.required_role
        )


class IsOrganizer(_RolePermission):
    required_role = "ORGANIZER"


class IsParticipant(_RolePermission):
    required_role = "PARTICIPANT"


class IsObserver(_RolePermission):
    required_role = "OBSERVER"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.is_staff or getattr(user, "role", None) == "ADMIN")
        )
