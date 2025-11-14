from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to authenticated users
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user is admin
        return request.user.is_staff or (hasattr(request.user, 'role') and request.user.role.name == 'admin')


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Check if user is admin
        if request.user.is_staff or (hasattr(request.user, 'role') and request.user.role.name == 'admin'):
            return True

        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False

