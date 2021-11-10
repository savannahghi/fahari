from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class CanExportData(BasePermission):
    """Allows access only to users who have the export data permission."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm("can_export_data")
        )


class CanImportData(BasePermission):
    """Allow access only to users who have the import data permission."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm("can_import_data")
        )
