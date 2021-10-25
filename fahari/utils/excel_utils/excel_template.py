from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, TypeVar

from openpyxl import Workbook

from .excel_io import ProgressCallback

DT = TypeVar("DT")


class ExcelIOTemplate(Generic[DT], metaclass=ABCMeta):
    """Represents an object that knows the layout of an excel workbook.

    This includes the formatting, worksheets, cell placement and cell
    validation options of a workbook. For simple use cases, an `ExcelIO`
    instance might be sufficient to describe both the *io* operations
    and layout options and as such, this class might not be required.
    """

    @abstractmethod
    def generate_input_template(
        self, workbook: Workbook, progress_callback: Optional[ProgressCallback]
    ) -> None:
        """Prepare the given workbook for input."""
        ...

    @abstractmethod
    def read(self, workbook: Workbook, progress_callback: Optional[ProgressCallback] = None) -> DT:
        """Retrieve and return data from the given workbook."""
        ...

    @abstractmethod
    def render(
        self, data: DT, workbook: Workbook, progress_callback: Optional[ProgressCallback] = None
    ) -> None:
        """Render the given data in the given workbook."""
        ...
