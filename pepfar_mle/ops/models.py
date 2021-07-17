from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from pepfar_mle.common.models import AbstractBase, Facility, System
from pepfar_mle.users.models import User


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

    class Meta:
        ordering = (
            "facility__name",
            "system__name",
            "-version",
            "-updated_by",
            "-created_by",
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

    def validate_resolved(self):
        error_msg = "resolved and resolved_by must both be set"
        if self.resolved is not None and self.resolved_by is None:
            raise ValidationError(error_msg)

        if self.resolved_by is not None and self.resolved is None:
            raise ValidationError(error_msg)

    class Meta:
        ordering = (
            "facility_system__facility__name",
            "facility_system__system__name",
            "-raised",
            "-resolved",
        )
