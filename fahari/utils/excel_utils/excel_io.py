from abc import ABCMeta, abstractmethod
from typing import Callable, Generic, TypeVar

from openpyxl import Workbook

DT = TypeVar("DT")

ProgressCallback = Callable[[int, int, float], None]


class ExcelIO(Generic[DT], metaclass=ABCMeta):
    """Describes the necessary API needed to work with Excel data.

    This abstract base class defines a set of operations that are needed in
    order to read, write and generate excel template files.
    """

    @abstractmethod
    def dump_data(self, data: DT, progress_callback: ProgressCallback = None) -> Workbook:
        """Write the given data to an excel workbook and return the workbook."""
        ...

    @abstractmethod
    def ingest_data(self, source: Workbook, progress_callback: ProgressCallback = None) -> DT:
        """Read and return data from an excel workbook."""
        ...

    @abstractmethod
    def generate_input_template(self, progress_callback: ProgressCallback = None) -> Workbook:
        """Make a new excel template that can be used for data input and return it.

        Once the generated template is filled with data, `self.ingest_data()`
        should be able to retrieve that data.
        """
        ...
