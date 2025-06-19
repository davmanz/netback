from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol Admin."""

    def has_permission(self, request, view):
        return request.user.role == "admin"


class IsOperator(BasePermission):
    """Permite acceso a operadores (pueden crear equipos y hacer backups manualmente)."""

    def has_permission(self, request, view):
        return request.user.role in ["admin", "operator"]


class IsViewer(BasePermission):
    """Permite solo visualizar datos."""

    def has_permission(self, request, view):
        return request.user.role in ["admin", "operator", "viewer"]
