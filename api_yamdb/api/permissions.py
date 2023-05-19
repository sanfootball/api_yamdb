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
    """Разрешение для админа или любого GET-запроса."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_staff)


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser


class AdminAndSuperUserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        del view
        if (request.user.is_staff or request.user.is_superuser) and request.user.is_authenticated:
            return True

#    def has_object_permission(self, request, view, obj):
#        del view
#        if obj.user.is_staff or obj.user.is_superuser:
#            return True


class AccessUsersMe(permissions.BasePermission):
    # def has_permission(self, request, view):
    #     del view
    #     if request.user.is_authenticated:
    #         return True

    def has_object_permission(self, request, view, obj):
        del view
        if (request.user.is_staff or request.user.is_superuser) and request.user.is_admin:
            return True
