from rest_framework.permissions import BasePermission

from apps.accounts.constants import PermissionMessages


class IsAdmin(BasePermission):
    message = PermissionMessages.ADMIN_ONLY

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.is_admin
        )


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)


class IsAnalystOrAbove(BasePermission):
    message = PermissionMessages.ANALYST_OR_ABOVE

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_analyst)


class IsViewerOrAbove(BasePermission):
    message = PermissionMessages.VIEWER_OR_ABOVE

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_viewer)


class IsAdminOrReadOnly(BasePermission):
    message = PermissionMessages.ADMIN_WRITE_ONLY

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.is_admin
