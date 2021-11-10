from typing import Sequence


class ProcessGoogleSheetRowError(RuntimeError):
    """Raised when processing a google sheet row fails."""

    def __init__(self, row: Sequence[str], row_index: int, *args, **kwargs):
        self.row: Sequence[str] = tuple(row)
        self.row_index: int = row_index
        super().__init__(*args, **kwargs)  # type: ignore
