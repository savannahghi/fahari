"""
A utility package composed of classes and functions for working with excel data.

The package contains the following abstract base classes; `ExcelIO` and
`ExcelIOTemplate` that together define an API for working with excel data.
`ExcelIO` defines an interface composed of all the basic operations needed
to read and write to excel workbooks and to generate excel templates used
for data input. `ExcelIOTemplate` on the other hand describes the layout of
an excel workbook including the formatting and cell validation options. For
simple use cases, an `ExcelIO` instance might be enough to describe both the
*io* operations and layout options and as such, an `ExcelIOTemplate` is not
always required.

Included also is a default implementation of the `ExcelIO` interface powered
by `DRF Serializers <https://www.django-rest-framework.org/api-guide/serializers/>`_
and a default `ExcelIOTemplate` that works with serializer data.
"""

from .drf_serializer_excel_io import (
    AuditSerializerExcelIO,
    DRFSerializerExcelIO,
    DRFSerializerExcelIOTemplate,
)
from .excel_io import ExcelIO
from .excel_template import ExcelIOTemplate

__all__ = [
    "AuditSerializerExcelIO",
    "DRFSerializerExcelIO",
    "DRFSerializerExcelIOTemplate",
    "ExcelIO",
    "ExcelIOTemplate",
]
