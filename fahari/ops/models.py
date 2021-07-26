from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils import timezone

from fahari.common.models import AbstractBase, Facility, System

User = get_user_model()


class TimeSheet(AbstractBase):
    """Staff daily time sheets."""

    date = models.DateField()
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


class ActivityLog(AbstractBase):
    activity = models.TextField(help_text="Activity as budgeted for")
    planned_date = models.DateField(help_text="Planned date for the activity")
    requested_date = models.DateField(help_text="Date requested")
    procurement_date = models.DateField(help_text="Date received by procurement")
    finance_approval_date = models.DateField(help_text="Date received by Finance for approvals")
    final_approval_date = models.DateField(help_text="Date approved by COP/DCOP/FAD")
    done_date = models.DateField(help_text="Date when activity/procurement done")
    invoiced_date = models.DateField(
        help_text="Date when payment invoice was submitted to Finance"
    )
    remarks = models.TextField()

    class Meta:
        ordering = (
            "-requested_date",
            "-planned_date",
            "-procurement_date",
        )


class SiteMentorship(AbstractBase):
    staff_member = models.ForeignKey(User, on_delete=models.PROTECT)
    day = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    site = models.ForeignKey(Facility, on_delete=models.PROTECT)
    objective = models.TextField()
    pick_up_point = models.TextField()
    drop_off_point = models.TextField()

    class Meta:
        ordering = (
            "-day",
            "-end",
            "-start",
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
    date = models.DateField()
    total = models.IntegerField()
    clients_booked = models.IntegerField()
    kept_appointment = models.IntegerField()
    missed_appointment = models.IntegerField()
    came_early = models.IntegerField()
    unscheduled = models.IntegerField()
    new_ft = models.IntegerField()
    ipt_new_adults = models.IntegerField()
    ipt_new_paeds = models.IntegerField()

    @property
    def appointment_keeping(self):
        if self.clients_booked == 0:
            return 0

        return (self.kept_appointment / self.clients_booked) * 100


class OperationalArea(AbstractBase):
    """List of program areas."""

    name = models.CharField(max_length=64)
    description = models.TextField()


class Activity(AbstractBase):
    area = models.ForeignKey(OperationalArea, on_delete=models.PROTECT)
    name = models.CharField(max_length=64)
    description = models.TextField()
    responsibility = models.ForeignKey(User, on_delete=models.PROTECT)
    deadline = models.DateField()
    is_complete = models.BooleanField(default=False)


class WeeklyProgramUpdate(AbstractBase):
    """
    Record of updates made at the weekly "touch base" meetings.
    """

    date = models.DateField()
    attendees = ArrayField(
        models.TextField(),
    )
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    comments = models.TextField()


class StockReceiptVerification(AbstractBase):
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    description = models.TextField()
    pack_size = models.TextField()
    delivery_note_number = models.CharField(max_length=64)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=4)
    batch_number = models.CharField(max_length=64)
    expiry_date = models.DateField()
    comments = models.TextField()
