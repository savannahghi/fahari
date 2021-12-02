from typing import Any, Optional


class MetadataEntryProcessingError(RuntimeError):
    """A generic error raised to indicate that a metadata entry processor run was unsuccessful."""

    def __init__(
        self,
        metadata_entry_name: str,
        metadata_entry_value: Any,
        error_message: Optional[str] = None,
        *args
    ):
        self.metadata_entry_name = metadata_entry_name
        self.metadata_entry_value = metadata_entry_value
        self._error_message = error_message or (
            'Error while processing metadata entry "%s" with value "%s".'
            % (self.metadata_entry_name, str(self.metadata_entry_value))
        )
        super(MetadataEntryProcessingError, self).__init__(self._error_message, *args)
