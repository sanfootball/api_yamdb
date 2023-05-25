from rest_framework import permissions


class IsAuthorOrModerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (
                request.user.role == 'admin'
                or request.user.role == 'moderator'
                or (request.user.role == 'user'
                    and request.user == obj.author)
            )
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для админа или любого GET-запроса."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.role == 'admin')


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser


class AccessUsersMe(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_staff
                or request.user.is_superuser) and (
                    request.user.is_admin)
