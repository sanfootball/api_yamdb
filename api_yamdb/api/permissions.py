from rest_framework import permissions


class IsAuthorOrModerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                request.user.is_admin or request.user.is_moderator
                or (request.user.is_user
                    and request.user == obj.author)
            )
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS) or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrModerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                request.user.is_admin or request.user.is_moderator
                or (request.user.is_user
                    and request.user == obj.author)
            )
        return False


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
