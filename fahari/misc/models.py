from datetime import datetime
from typing import Any, Callable, Dict, Optional, Sequence, Type, TypedDict, cast

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.fields import DateField, DateTimeField, Field
from django.db.models.fields.related import RelatedField
from django.utils import timezone

from fahari.common.models import AbstractBase
from fahari.common.utils.administrative_unit_utils import get_counties
from fahari.ops.models import StockReceiptVerification
from fahari.utils.excel_utils.google_sheets_excel_utils import read_spreadsheet

from .exceptions import ProcessGoogleSheetRowError

ProgressCallback = Callable[[int, int, float], None]


class SheetColumnToModelFieldMappingMetadata(TypedDict):
    """Structure of the sheet column to model field mapping metadata dictionary."""

    column_index: int
    datetime_format: Optional[str]
    default_value: Optional[Any]
    lookup: Optional[str]
    optional: Optional[bool]
    value_mappings: Optional[Dict[str, Any]]


class SheetToDBMappingsMetadata(AbstractBase):
    """Metadata on google sheet columns to model field mappings."""

    name = models.CharField(max_length=255, verbose_name="A descriptive name for a mapping.")
    mappings_metadata = models.JSONField(default=dict, help_text="Sheet to DB mappings")
    version = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return "{} v{}".format(self.name, self.version) if self.version else self.name

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "Sheet to db mappings metadata"


class AbstractGoogleSheetToDjangoModelAdapter(AbstractBase):
    """Consumes a Google sheet spreadsheet and persists the data using a django model."""

    target_model = models.ForeignKey(ContentType, models.PROTECT)
    sheet_id = models.TextField(verbose_name="Google Spreadsheet Id")
    data_sheet_name = models.CharField(
        max_length=255,
        help_text="The name of the sheet contain the data to be ingested.",
    )
    first_column = models.CharField(max_length=3, default="A")
    last_column = models.CharField(max_length=3)
    position = models.PositiveIntegerField(
        default=1,
        help_text="The last ingest row. The next ingest will begin at the row after this one.",
    )
    field_mappings_meta = models.ForeignKey(SheetToDBMappingsMetadata, on_delete=models.PROTECT)
    last_ingested = models.DateTimeField(null=True, blank=True, editable=False)

    def do_persist_sheet_row(  # noqa
        self, row_data: Dict[str, Any], model_class: Type[models.Model], **kwargs
    ) -> models.Model:
        """Perform the actual db persistence of google sheet row data."""

        return model_class._meta.default_manager.create(**row_data, **kwargs)

    def extract_sheet_value(  # noqa
        self,
        row: Sequence[str],
        field_mappings_metadata: SheetColumnToModelFieldMappingMetadata,
    ) -> str:
        """Get the sheet value given a row and field mappings metadata."""

        column_index = field_mappings_metadata["column_index"]
        default_value = field_mappings_metadata.get("default_value")
        optional = field_mappings_metadata.get("optional", False)
        return str(default_value) if optional and len(row) <= column_index else row[column_index]

    def get_next_ingest_range_name(self) -> str:
        """Return the range of the next ingest."""

        return "%s!%s%d:%s" % (
            self.data_sheet_name,
            self.first_column,
            self.position + 1,
            self.last_column,
        )

    @transaction.atomic
    def ingest_from_last_position(
        self, progress_callback: Optional[ProgressCallback], **extra_context
    ) -> int:
        """Read each row starting from the current position and persist it."""

        dummy_callback: ProgressCallback = lambda _, __, ___: None  # noqa
        progress_callback = progress_callback or dummy_callback
        rows = read_spreadsheet(self.sheet_id, self.get_next_ingest_range_name())
        total_rows = len(rows)
        try:
            for offset, row in enumerate(rows):
                self.process_add_persist_sheet_row(row, **extra_context)
                progress_callback(offset + 1, total_rows, ((offset + 1) / total_rows) * 100.0)
        except Exception as exp:
            row_index = self.position + offset + 1  # noqa
            raise ProcessGoogleSheetRowError(
                row, row_index, "Error processing row %d" % row_index  # noqa
            ) from exp

        self.position += total_rows
        self.last_ingested = timezone.now()
        self.save()
        return total_rows

    def process_add_persist_sheet_row(self, row: Sequence[str], **extra_context) -> None:
        """Clean, validate and persist a stock verification receipt from a spreadsheet row."""

        data: Dict[str, Any] = {}
        mappings_meta: Dict[str, SheetColumnToModelFieldMappingMetadata]
        mappings_meta = self.field_mappings_meta.mappings_metadata
        model_class: Type[models.Model] = cast(Type[models.Model], self.target_model.model_class())
        for field_name, meta in mappings_meta.items():
            field: Field = next(filter(lambda f: f.name == field_name, model_class._meta.fields))
            sheet_value = self.extract_sheet_value(row, meta)
            try:
                db_value = self.to_db_value(sheet_value, field, meta)
                data[field_name] = db_value
            except Exception as exp:
                raise ValueError(
                    '"%s" is not a valid value for field "%s"' % (sheet_value, field_name)
                ) from exp

        extra_kwargs = extra_context.get("extra_kwargs", {})
        self.do_persist_sheet_row(data, model_class, **extra_kwargs)

    def to_db_value(  # noqa
        self,
        sheet_value: str,
        field: Field,
        field_mappings_metadata: SheetColumnToModelFieldMappingMetadata,
    ) -> Any:
        """Convert a value in a google sheet column to it's db value equivalent."""

        value_mappings = cast(Dict[str, Any], field_mappings_metadata.get("value_mappings", {}))
        db_value = value_mappings.get(sheet_value, sheet_value)
        if isinstance(field, RelatedField):
            lookup: str = cast(str, field_mappings_metadata.get("lookup", field.name))
            manager: models.Manager = field.related_model._base_manager  # type: ignore
            qs_filter: Dict[str, Any] = {lookup: db_value}
            return manager.get(**qs_filter)
        if isinstance(field, (DateField, DateTimeField)):
            datetime_format: Optional[str] = field_mappings_metadata.get("datetime_format")
            if datetime_format is not None:  # pragma: no branch
                db_value = datetime.strptime(db_value, datetime_format)

        return field.clean(db_value, None)

    class Meta(AbstractBase.Meta):
        abstract = True


class StockVerificationReceiptsAdapter(AbstractGoogleSheetToDjangoModelAdapter):
    """Metadata about stock verification reports data ingest."""

    county = models.CharField(max_length=65, choices=get_counties(), unique=True)

    def save(self, *args, **kwargs):
        """Override the default behaviour to make sure that target model is set correctly.

        That is, make sure that the `target_model` field always refers to the
        `StockReceiptVerification`.
        """

        self.target_model = ContentType.objects.get(
            app_label=StockReceiptVerification._meta.app_label,
            model=StockReceiptVerification._meta.model_name,
        )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.get_county_display()  # noqa
