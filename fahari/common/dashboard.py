from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from fahari.ops.models import DailyUpdate, Questionnaire

from .models import Facility

User = get_user_model()


def get_fahari_facilities_queryset():
    return Facility.objects.fahari_facilities().order_by(
        "name",
        "county",
        "mfl_code",
    )


def get_mentorship_questionnaires_queryset():
    return Questionnaire.objects.all()


def get_active_facility_count(user):
    return (
        Facility.objects.fahari_facilities()
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
