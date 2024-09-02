from rest_framework.permissions import BasePermission

class IsIncidentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.reporter == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
