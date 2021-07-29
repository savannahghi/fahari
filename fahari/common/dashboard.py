from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from fahari.ops.models import DailyUpdate

from .constants import WHITELIST_COUNTIES
from .models import Facility

User = get_user_model()


def get_fahari_facilities_queryset():
    return Facility.objects.filter(
        is_fahari_facility=True,
        operation_status="Operational",
        county__in=WHITELIST_COUNTIES,
        active=True,
    )


def get_active_facility_count(user):
    return (
        get_fahari_facilities_queryset()
        .filter(
            organisation=user.organisation,
        )
        .count()
    )


def get_open_ticket_count(user):
    from fahari.ops.models import FacilitySystemTicket

    return FacilitySystemTicket.objects.filter(
        resolved__isnull=True,
        active=True,
        organisation=user.organisation,
    ).count()


def get_active_user_count(user):
    return User.objects.filter(
        is_approved=True,
        approval_notified=True,
        organisation=user.organisation,
    ).count()


def get_appointments_mtd(user):
    today = timezone.datetime.today()
    year = today.year
    month = today.month
    qs = DailyUpdate.objects.filter(
        active=True,
        date__year=year,
        date__month=month,
        organisation=user.organisation,
    ).aggregate(Sum("total"))
    return qs["total__sum"]
