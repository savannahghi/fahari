from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union, cast

from crispy_forms.utils import render_crispy_form
from django_filters.rest_framework.backends import DjangoFilterBackend
from openpyxl import Workbook
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.relations import ManyRelatedField, PrimaryKeyRelatedField
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from fahari.common.permissions import CanExportData
from fahari.common.renderers import ExcelIORenderer
from fahari.utils.excel_utils import (
    AuditSerializerExcelIO,
    DRFSerializerExcelIO,
    DRFSerializerExcelIOTemplate,
    ExcelIO,
    ExcelIOTemplate,
)

EIO = TypeVar("EIO", bound=ExcelIO, covariant=True)
EIO_T = TypeVar("EIO_T", bound=ExcelIOTemplate, covariant=True)


class ExcelIOMixin(Generic[EIO, EIO_T], GenericViewSet):
    """Mixin that adds excel io operations to a view."""

    excel_io_class: Optional[Type[EIO]] = None
    excel_io_template_class: Optional[Type[EIO_T]] = None
    filename: Optional[str] = None

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(DjangoModelPermissions, CanExportData),
        renderer_classes=(ExcelIORenderer,),
    )
    def dump_data(self, request: Request, pk=None) -> Response:
        """Export data in excel format."""

        workbook = self.perform_dump_data(request)
        return Response(workbook, status=status.HTTP_200_OK)

    def finalize_response(
        self, request: Request, response: Response, *args: Any, **kwargs: Any
    ) -> Response:
        """Override the base implementation to add a filename to the returned file."""

        response = super().finalize_response(request, response, *args, **kwargs)
        if isinstance(response, Response) and response.accepted_renderer.format == "xlsx":  # noqa
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(),
            )

        return response

    def get_excel_io(self, **kwargs) -> EIO:
        """Return an excel io object to be used in excel input/output operations."""

        excel_io_class = self.get_excel_io_class()
        default_kwargs = self.get_excel_io_kwargs()
        default_kwargs.update(kwargs)
        return excel_io_class(**default_kwargs)  # type: ignore

    def get_excel_io_kwargs(self) -> Dict[str, Any]:
        """Return kwargs to be used when initializing an excel io instance."""

        return {"template_class": self.get_excel_io_template_class()}

    def get_excel_io_class(self) -> Type[EIO]:
        """Return a class to use for the excel io. Defaults to using `self.excel_io_class`."""

        assert self.excel_io_class is not None, (
            "'%s' should either include a `excel_io_class` attribute, "
            "or override the `get_excel_io_class()` method." % self.__class__.__name__
        )
        return self.excel_io_class

    def get_excel_io_template_class(self) -> Optional[Type[EIO_T]]:
        """Return a class to use for the excel io template.

        Defaults to using `self.excel_io_template_class`.
        """

        return self.excel_io_template_class

    def get_filename(self) -> str:
        """Return the filename to be used for the exported excel file."""

        return self.filename or "%s.xlsx" % self.get_queryset().model._meta.verbose_name_plural

    def perform_dump_data(self, request: Request) -> Workbook:  # pragma: nocover
        """Perform the actual dump data operation and return a workbook with the results."""

        excel_io = self.get_excel_io()
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return excel_io.dump_data(serializer.data)


class DRFSerializerExcelIOMixin(
    ExcelIOMixin[DRFSerializerExcelIO, DRFSerializerExcelIOTemplate], DjangoFilterBackend
):
    """Mixins for excel io operations powered by DRF Serializer."""

    excel_io_class = DRFSerializerExcelIO
    excel_io_serializer_class: Optional[Type[Serializer]] = None
    excel_io_template_class = DRFSerializerExcelIOTemplate
    nested_entries_delimiter: Optional[str] = None

    @action(detail=False, methods=["GET"])
    def get_available_fields(self, request: Request, pk=None) -> Response:
        """Return a list of all the fields that make up the excel column headers.

        The response returned by this action can be used as a data source for
        a html element used to select/request data from specific fields.
        """

        all_fields = self.retrieve_available_fields(request)
        return Response(all_fields, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], renderer_classes=(StaticHTMLRenderer,))
    def get_filter_form(self, request: Request, pk=None) -> Response:
        """Return a html form containing additional filters for this view."""

        form = self.retrieve_filter_form(request)
        return Response(form, status=status.HTTP_200_OK)

    def get_excel_io_kwargs(self) -> Dict[str, Any]:
        """Return kwargs to be used when initializing an excel io instance.

        Extend the default implementation to also include a serializer class.
        """

        kwargs = super().get_excel_io_kwargs()
        kwargs["context"] = self.get_serializer_context()
        kwargs["nested_entries_delimiter"] = self.get_nested_entries_delimiter()
        kwargs["serializer_class"] = self.get_excel_io_serializer_class()
        return kwargs

    def get_excel_io_serializer_class(self) -> Type[Serializer]:
        """Return the serializer class to be used for excel io operations.

        Defaults to using `self.excel_io_serializer_class` if present or
        `self.get_serializer_class()` otherwise.
        """

        return self.excel_io_serializer_class or self.get_serializer_class()

    def get_nested_entries_delimiter(self) -> str:
        """Return the delimiter used to separate nested entries."""

        return self.nested_entries_delimiter or "::"

    def perform_dump_data(self, request: Request) -> Workbook:
        """Override the default implementation to capture the requested dump fields."""

        dump_fields = filter(
            lambda field: field != "*",  # Remove the root field if present
            request.query_params.getlist("dump_fields"),
        )
        excel_io = self.get_excel_io(dump_fields=dump_fields)
        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        return excel_io.dump_data(serializer.data)

    def retrieve_available_fields(self, request: Request) -> List[Dict[str, Any]]:
        """Performs the actual retrieval of all the available fields for a given excel io.

        This particular implementation returns values that can be used to
        drive a jstree (https://www.jstree.com/) component.
        """

        nested_entries_delimiter = self.get_nested_entries_delimiter()

        # Visit each field and map it to an appropriate field descriptor.
        def visit(fields: Dict[str, Any], parent_key="") -> List[Dict[str, Union[str, Any]]]:
            results = []
            for key, val in fields.items():
                if isinstance(val, (ManyRelatedField, PrimaryKeyRelatedField)):
                    # Skip primary key fields and many to many fields
                    continue
                new_key = parent_key + nested_entries_delimiter + key if parent_key else key
                new_value = {
                    "icon": "fas fa-folder",
                    "id": new_key,
                    "text": key.capitalize().replace("_", " "),
                }
                if isinstance(val, dict):
                    new_value["children"] = visit(val, new_key)
                results.append(new_value)
            return results

        return [
            {
                "children": visit(self.get_excel_io().get_fields()),
                "icon": "fas fa-database",
                "id": "*",
                "state": {"opened": True, "selected": True},
                "text": "All",
            }
        ]

    def retrieve_filter_form(self, request: Request) -> str:
        """Performs the actual retrieval of the form containing filters for this view."""

        filterset = self.get_filterset(request, self.get_queryset(), self)
        if not filterset:
            return "<p>No filters were found.</p>"
        return render_crispy_form(filterset.form)  # pragma: nocover


class AuditSerializerExcelIOMixin(DRFSerializerExcelIOMixin):
    """Mixin for excel io operations powered by `AuditMixin`.

    This mixin exists to make sure that audit field's don't leak to
    the exported data.
    """

    excel_io_class = AuditSerializerExcelIO

    def get_audit_field_names(self) -> Sequence[str]:
        """Return the names of the audit field names to be excluded."""

        excel_io: AuditSerializerExcelIO = cast(AuditSerializerExcelIO, self.get_excel_io())
        return excel_io.get_audit_field_names()

    def retrieve_filter_form(self, request: Request) -> str:
        """Performs the actual retrieval of the form containing filters for this view.

        Replaces the base implementation by returning a form that excludes
        filters referencing audit fields.
        """

        filterset = self.get_filterset(request, self.get_queryset(), self)
        if not filterset:  # pragma: nocover
            return "<p>No filters were found.</p>"

        audit_fields = tuple(self.get_audit_field_names()) + ("bubble_record", "combobox")
        for audit_field in audit_fields:
            filterset.filters.pop(audit_field, None)
        return render_crispy_form(filterset.form)
