from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'create', 'obtain_auth_token']:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'update_password', 'delete_token']:
            return request.user.is_authenticated
        return True
