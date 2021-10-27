from typing import Any, Dict, Generic, TypeVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from fahari.common.permissions import CanImportData
from fahari.common.views import BaseView

from .exceptions import ProcessGoogleSheetRowError
from .models import AbstractGoogleSheetToDjangoModelAdapter, StockVerificationReceiptsAdapter
from .serializers import StockVerificationReceiptsAdapterSerializer

A = TypeVar("A", bound=AbstractGoogleSheetToDjangoModelAdapter, covariant=True)


class GoogleSheetToDjangoModelAdapterMixin(Generic[A], GenericViewSet):
    """Mixin that allows data to be ingested from a Google Sheets spreadsheet using an adapter."""

    @action(
        detail=True, methods=["POST"], permission_classes=(DjangoModelPermissions, CanImportData)
    )
    def ingest_from_last_position(self, request: Request, pk=None) -> Response:
        """Read, process and persist data from a Google Sheets spreadsheet."""

        adapter = self.get_adapter_instance(request, pk)
        adapter_context = self.get_adapter_context()
        try:
            ingested_rows = adapter.ingest_from_last_position(None, **adapter_context)
        except ProcessGoogleSheetRowError as exp:
            error_details = {"row_index": exp.row_index}
            error_messages = []
            while exp is not None:
                error_messages.append(str(exp))
                exp = exp.__cause__  # type: ignore
            error_details["error_messages"] = error_messages

            return Response(error_details, status=status.HTTP_400_BAD_REQUEST)

        return Response({"ingested_rows": ingested_rows}, status=status.HTTP_200_OK)

    def get_adapter_context(self) -> Dict[str, Any]:
        """Return extra context to be injected in an adapter's `ingest_from_last_position` method.

        Subclasses can override this method to add or change the returned
        context dict.
        """

        return {
            "extra_kwargs": {
                "created_by": self.request.user.pk,
                "organisation": self.request.user.organisation,  # noqa
                "updated_by": self.request.user.pk,
            }
        }

    def get_adapter_instance(self, request: Request, pk) -> A:
        """Return an adapter instance to be used for the actual data ingest given a request."""

        return self.get_object()


class StockVerificationReceiptsAdapterView(
    BaseView, GoogleSheetToDjangoModelAdapterMixin[StockVerificationReceiptsAdapter]
):
    """StockVerificationReceiptsAdapter API."""

    queryset = StockVerificationReceiptsAdapter.objects.active()
    serializer_class = StockVerificationReceiptsAdapterSerializer
