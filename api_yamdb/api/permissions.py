from rest_framework import permissions


class IsAuthorOrModerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST' and request.user.is_authenticated:
            return True
        if request.method == 'PATCH' or request.method == 'DELETE':
            if request.user == obj.author:
                return True
            if request.user.role == 'admin' or (
                    request.user.role == 'moderator'):
                return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для админа или любого GET-запроса."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.role == 'admin')


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser


class AccessUsersMe(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        del view
        if (request.user.is_staff or request.user.is_superuser) and (
                request.user.is_admin):
            return True
