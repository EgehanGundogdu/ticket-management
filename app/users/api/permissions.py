from rest_framework import permissions


class CompanyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_company_admin)
