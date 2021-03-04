from rest_framework import permissions


class IsUserNotBlocked(permissions.BasePermission):
    message = 'User blocked by administrator.'

    def has_permission(self, request, view):
        return bool(request.user and not request.user.blocked)
