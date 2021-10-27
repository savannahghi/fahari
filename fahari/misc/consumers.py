from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from channels.generic.websocket import JsonWebsocketConsumer

from .exceptions import ProcessGoogleSheetRowError
from .models import AbstractGoogleSheetToDjangoModelAdapter, StockVerificationReceiptsAdapter

A = TypeVar("A", bound=AbstractGoogleSheetToDjangoModelAdapter, covariant=True)
ProgressCallback = Callable[[int, int, float], None]


class AbstractGoogleSheetToDjangoModelAdapterConsumer(Generic[A], JsonWebsocketConsumer):
    """Read, process and persist data from a Google Sheets spreadsheet."""

    def connect(self) -> None:
        self.user = self.scope["user"]  # noqa
        # Ensure that the user has permissions to import data
        if not self.user.has_perm("can_import_data"):
            self.close(code=1008)
        self.accept()

    def receive_json(self, content: Any, **kwargs) -> None:
        adapter = self.get_adapter(content)
        try:
            ingested_rows = adapter.ingest_from_last_position(
                progress_callback=self.get_progress_callback(), **self.get_adapter_context()
            )
        except ProcessGoogleSheetRowError as exp:
            error_details = {"row_index": exp.row_index}
            error_messages = []
            while exp is not None:
                error_messages.append(str(exp))
                exp = exp.__cause__  # type: ignore
            error_details["error_messages"] = error_messages
            self.send_data("error", error_details)
            return

        self.send_data("success", {"ingested_rows": ingested_rows})  # noqa

    def send_data(self, data_type: str, data_content: Any) -> None:
        """Send the given data of to the party on the other end of this connection."""

        self.send_json({"type": data_type, "data": data_content})

    def get_adapter(self, content: Any) -> A:
        """Return an adapter instance given input."""

        raise NotImplementedError("`get_adapter` must be implemented.")

    def get_adapter_context(self) -> Dict[str, Any]:
        """Return extra context to be injected in an adapter's `ingest_from_last_position` method.

        Subclasses can override this method to add or change the returned
        context dict.
        """

        return {
            "extra_kwargs": {
                "created_by": self.user.pk,
                "organisation": self.user.organisation,  # noqa
                "updated_by": self.user.pk,
            }
        }

    def get_progress_callback(self) -> Optional[ProgressCallback]:
        """Optionally return a function that acts a progress callback."""

        def simple_progress_callback(current: int, total: int, percentage: float) -> None:
            """Send progress data through a web-socket to the client on the other end."""

            self.send_data(
                "progress", {"current": current, "total": total, "percentage": percentage}
            )

        return simple_progress_callback


class StockVerificationReceiptsAdapterConsumer(
    AbstractGoogleSheetToDjangoModelAdapterConsumer[StockVerificationReceiptsAdapter]
):
    """StockVerificationReceiptsAdapter consumer."""

    def get_adapter(self, content: Any) -> A:
        adapter: str = content["adapter"]
        return StockVerificationReceiptsAdapter.objects.active().get(pk=adapter)
