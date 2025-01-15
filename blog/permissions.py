from rest_framework import permissions

class IsAuthor(permissions.BasePermission):
    """
    Custom permission to only allow the author of the blog to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
