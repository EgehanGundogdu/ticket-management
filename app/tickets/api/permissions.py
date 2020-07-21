from rest_framework import permissions


class TicketUserTypePermission(permissions.BasePermission):
    """if user staff. cannot create new ticket!"""

    def has_permission(self, request, view):
        if request.user.is_staff and view.action == "create":
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or obj.company.leader == request.user

