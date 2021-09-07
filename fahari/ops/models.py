from datetime import time

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError, InternalError, ProgrammingError
from django.urls import reverse_lazy
from django.utils import timezone

from fahari.common.models import AbstractBase, Facility, Organisation, System, get_directory

User = get_user_model()

DEFAULT_COMMODITY_CODE = "OTHER"
DEFAULT_COMMODITY_NAME = "Other (please specify)"
DEFAULT_COMMODITY_PK = "bb5043a6-2a3d-4dea-95d1-72e7e0d274cf"


def default_start_time():
    return time(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone())


def default_end_time():
    return time(hour=18, minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone())


def default_commodity():
    """The commodity FK in the stock receipt model was introduced late.

    In order for migrations on the existing database to work, this function
    (used as a default callable on the field) initializes a sensible default
    for existing rows.
    """
    try:
        with transaction.atomic():
            com, _ = Commodity.objects.get_or_create(
                code=DEFAULT_COMMODITY_CODE,
                defaults={
                    "organisation": Organisation.objects.first(),
                    "pk": DEFAULT_COMMODITY_PK,
                    "name": DEFAULT_COMMODITY_NAME,
                },
            )
            return com.pk
    except (ProgrammingError, InternalError, IntegrityError):  # pragma: nocover  # pragma: noqa
        # this allows migrations against empty databases to work
        # it also allows migrations against existing databases to work
        return DEFAULT_COMMODITY_PK


class TimeSheet(AbstractBase):
    """Staff daily time sheets."""

    date = models.DateField(default=timezone.datetime.today)
    activity = models.TextField()
    output = models.TextField()
    hours = models.IntegerField()
    location = models.TextField()
    staff = models.ForeignKey(User, on_delete=models.PROTECT, related_name="timesheet_staff")
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    model_validators = ["validate_approval"]

    @property
    def is_full_day(self):
        return self.hours >= 8

    @property
    def is_approved(self):
        return self.approved_at is not None

    def __str__(self) -> str:
        return f"Time sheet: {self.activity} ({self.date})"

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:timesheet_update", kwargs={"pk": self.pk})
        return update_url

    def validate_approval(self):
        error_msg = "approved_at and approved_by must both be set"
        if self.approved_at is not None and self.approved_by is None:
            raise ValidationError(error_msg)

        if self.approved_by is not None and self.approved_at is None:
            raise ValidationError(error_msg)

    class Meta:
        ordering = (
            "-date",
            "-approved_at",
            "staff__name",
        )
        unique_together = (
            "staff",
            "date",
        )
        permissions = [
            ("can_approve_timesheet", "Can Approve Timesheet"),
        ]


class FacilitySystem(AbstractBase):
    """A registry of systems and versions for different facilities."""

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    system = models.ForeignKey(System, on_delete=models.PROTECT)
    version = models.CharField(max_length=64)

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:version_update", kwargs={"pk": self.pk})
        return update_url

    @property
    def facility_name(self):
        return self.facility.name

    @property
    def system_name(self):
        return self.system.name

    def __str__(self):
        return f"{self.facility_name} - {self.system_name}, version {self.version}"

    class Meta:
        ordering = (
            "facility__name",
            "system__name",
            "-version",
            "-updated",
            "-created",
        )
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "system", "version"],
                name="unique_together_facility_and_system_and_version",
            )
        ]


class FacilitySystemTicket(AbstractBase):
    """Tickets raised against specific tickets and versions."""

    facility_system = models.ForeignKey(FacilitySystem, on_delete=models.PROTECT)
    details = models.TextField()
    raised = models.DateTimeField(default=timezone.now)
    raised_by = models.TextField()
    resolved = models.DateTimeField(null=True, blank=True)
    resolved_by = models.TextField(null=True, blank=True)
    resolve_note = models.TextField(null=True, blank=True)

    model_validators = ["validate_resolved"]

    @property
    def is_open(self):
        return self.resolved is None

    @property
    def facility_system_name(self):
        return (
            f"Facility: {self.facility_system.facility.name}; "
            + f"System: {self.facility_system.system.name}; "
            + f"Version: {self.facility_system.version}"
        )

    @property
    def is_resolved(self):
        return self.resolved is not None

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:ticket_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self):
        return f"{self.facility_system_name} ({self.details})"

    def validate_resolved(self):
        error_msg = "resolved and resolved_by must both be set"
        if self.resolved is not None:
            if self.resolved_by is None or self.resolved_by == "":
                raise ValidationError(error_msg)

    class Meta:
        ordering = (
            "facility_system__facility__name",
            "facility_system__system__name",
            "-raised",
            "-resolved",
        )
        permissions = [
            ("can_resolve_ticket", "Can Resolve Ticket"),
        ]


class ActivityLog(AbstractBase):
    activity = models.TextField(help_text="Activity as budgeted for")
    planned_date = models.DateField(
        help_text="Planned date for the activity", default=timezone.datetime.today
    )
    requested_date = models.DateField(help_text="Date requested", default=timezone.datetime.today)
    procurement_date = models.DateField(
        help_text="Date received by procurement", default=timezone.datetime.today
    )
    finance_approval_date = models.DateField(
        help_text="Date received by Finance for approvals", default=timezone.datetime.today
    )
    final_approval_date = models.DateField(
        help_text="Date approved by COP/DCOP/FAD", default=timezone.datetime.today
    )
    done_date = models.DateField(
        help_text="Date when activity/procurement done", default=timezone.datetime.today
    )
    invoiced_date = models.DateField(
        help_text="Date when payment invoice was submitted to Finance",
        default=timezone.datetime.today,
    )
    remarks = models.TextField()

    def __str__(self) -> str:
        return self.activity

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:activity_log_update", kwargs={"pk": self.pk})
        return update_url

    class Meta:
        ordering = (
            "-planned_date",
            "-requested_date",
            "-procurement_date",
        )


class SiteMentorship(AbstractBase):
    staff_member = models.ForeignKey(User, on_delete=models.PROTECT)
    day = models.DateField(default=timezone.datetime.today)
    duration = models.DurationField(
        help_text="HH:MM:SS e.g '08:00:00' for 8 hours",
        default="08:00:00",
    )
    site = models.ForeignKey(Facility, on_delete=models.PROTECT)
    objective = models.TextField()
    pick_up_point = models.TextField()
    drop_off_point = models.TextField()

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:site_mentorship_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self) -> str:
        return (
            f"Site Mentorship: {self.staff_member.name} "
            + f"at {self.site.name} on {self.day} (for {self.duration})"
        )

    class Meta:
        ordering = (
            "-day",
            "site__name",
        )


class DailyUpdate(AbstractBase):
    """
    Daily updates from facilities.

    e.g

        16/6/2021
        Clients booked -18
        Kept appointment -17
        Came early -0
        Total -17
        Missed appointment- 1
        Unscheduled - 36
        Appointment keeping - 94%
        New FT - 0
        IPT New adults- 0
        IPT New paeds  - 0
    """

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.datetime.today)
    total = models.IntegerField(default=0)
    clients_booked = models.IntegerField(default=0)
    kept_appointment = models.IntegerField(default=0)
    missed_appointment = models.IntegerField(default=0)
    came_early = models.IntegerField(default=0)
    unscheduled = models.IntegerField(default=0)
    new_ft = models.IntegerField(default=0)
    ipt_new_adults = models.IntegerField(default=0)
    ipt_new_paeds = models.IntegerField(default=0)

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:daily_update_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self) -> str:
        return f"Daily Update: {self.facility.name} - {self.date}"

    @property
    def appointment_keeping(self):
        if self.clients_booked == 0:
            return 0

        return (self.kept_appointment / self.clients_booked) * 100

    class Meta:
        ordering = (
            "-date",
            "facility__name",
        )
        unique_together = (
            "facility",
            "date",
        )


class Commodity(AbstractBase):
    """Model to record lab and pharmacy commodity names and codes."""

    name = models.CharField(max_length=128, null=False, blank=False, unique=True)
    code = models.CharField(max_length=64, null=False, blank=False, unique=True)
    description = models.TextField(default="-", null=False, blank=False)
    is_lab_commodity = models.BooleanField(default=False)
    is_pharmacy_commodity = models.BooleanField(default=False)
    unit_of_measure = models.ForeignKey("UoM", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:commodity_update", kwargs={"pk": self.pk})
        return update_url

    class Meta(AbstractBase.Meta):
        verbose_name_plural = "commodities"


class StockReceiptVerification(AbstractBase):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    commodity = models.ForeignKey(Commodity, on_delete=models.PROTECT, default=default_commodity)
    description = models.TextField(default="-")
    unit_of_measure = models.ForeignKey(
        "UoM", on_delete=models.PROTECT, null=True, blank=True, verbose_name="Pack size"
    )
    delivery_note_number = models.CharField(max_length=64)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=4)
    batch_number = models.CharField(max_length=64)
    delivery_date = models.DateField(default=timezone.datetime.today)
    expiry_date = models.DateField(default=timezone.datetime.today)
    delivery_note_image = models.ImageField(
        upload_to="ops/stock_receipts/delivery_notes/",
        null=True,
        blank=True,
        verbose_name="Delivery note photograph",
    )
    comments = models.TextField()

    def __str__(self):
        return f"{self.facility.name} (Delivery Note: {self.delivery_note_number})"

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:stock_receipt_verification_update", kwargs={"pk": self.pk})
        return update_url


class OperationalArea(AbstractBase):
    """List of program areas."""

    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return self.name


class Activity(AbstractBase):
    area = models.ForeignKey(OperationalArea, on_delete=models.PROTECT)
    name = models.CharField(max_length=64)
    description = models.TextField()
    responsibility = models.ForeignKey(User, on_delete=models.PROTECT)
    deadline = models.DateField()
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class WeeklyProgramUpdate(AbstractBase):
    """
    Record of updates made at the weekly "touch base" meetings.
    """

    title = models.CharField(max_length=255, default="-")
    attendees = ArrayField(
        models.TextField(),
        help_text="Use commas to separate attendees names",
    )

    description = models.TextField(default="-")
    attachment = models.FileField(upload_to=get_directory, null=True, blank=True)
    date = models.DateField(default=timezone.datetime.today)

    def __str__(self) -> str:
        return f"Weekly update: {self.date}, attended by {self.attendees}"

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:weekly_program_updates_update", kwargs={"pk": self.pk})
        return update_url


class WeeklyProgramUpdateDetail(AbstractBase):

    parent = models.ForeignKey(WeeklyProgramUpdate, on_delete=models.PROTECT)
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    comments = models.TextField()


class UoM(AbstractBase):
    """Measure by which items are maintained in inventory."""

    name = models.CharField("Unit of Measure", max_length=200)
    category = models.ForeignKey(
        "UoMCategory",
        on_delete=models.PROTECT,
        help_text="Conversion between Units of Measure can only "
        "occur if they belong to the same category.",
    )

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:uom_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self):
        return self.name


class UoMCategory(AbstractBase):
    """Inventory units of measure category."""

    class MeasureTypes(models.TextChoices):
        """The different types of measurements available."""

        LENGTH = "length", "Length"
        TIME = "time", "Time"
        UNIT = "unit", "Unit"
        VOLUME = "volume", "Volume"
        WEIGHT = "weight", "Weight"

    name = models.CharField(max_length=255)
    measure_type = models.CharField(
        max_length=50,
        choices=MeasureTypes.choices,
        help_text="Type of Measure",
    )

    def get_absolute_url(self):
        update_url = reverse_lazy("ops:uom_category_update", kwargs={"pk": self.pk})
        return update_url

    def __str__(self):
        return self.name
