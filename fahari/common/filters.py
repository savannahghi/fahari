"""Base filters."""
import django_filters
from django.db.models import Case, IntegerField, Value, When
from rest_framework import filters
from rest_framework.filters import SearchFilter

from .models import Facility, FacilityUser, System


class CommonFieldsFilterset(django_filters.FilterSet):
    """This is intended to be the base filter for most app filtersets."""

    search = SearchFilter()

    def inactive_records(self, queryset, field, value):
        """
        Select *inactive* records only.

        This function allows filtering of only the fields with active=False
        To display the inactive records the query param should be set to
        active=False or an equivalence as specified below
        """
        return queryset.filter(active=value)

    def bubble_record_to_top(self, queryset, field, value):
        """Ensure that the current record appears on top.

        This ensures that the record is available in select / comboboxes
        even if it is a 'deep' entry that would otherwise be buried by
        pagination.
        """
        ordering_filters = ("custom_order", "-updated", "-created")
        annotated_qs = queryset.annotate(
            custom_order=Case(
                When(pk=value, then=Value(0)),
                output_field=IntegerField(),
                default=Value(1),
            )
        ).order_by(*(ordering_filters))

        # guarantee that an entry with the supplied PK is *always* returned
        alternate_qs = (
            queryset.model.objects.filter(pk=value)
            .annotate(
                custom_order=Case(
                    When(pk=value, then=Value(0)),
                    output_field=IntegerField(),
                    default=Value(1),
                )
            )
            .order_by(*(ordering_filters))
        )
        return annotated_qs if annotated_qs.count() > 0 else alternate_qs

    active = django_filters.BooleanFilter(method="inactive_records")
    bubble_record = django_filters.UUIDFilter(method="bubble_record_to_top")
    combobox = django_filters.UUIDFilter(method="bubble_record_to_top")


class OrganisationFilterBackend(filters.BaseFilterBackend):
    """Users are only allowed to view records in their organisation."""

    def filter_queryset(self, request, queryset, view):
        """Filter all records that have an organisation field by user org."""
        return queryset.filter(organisation=request.user.organisation)


class FacilityFilter(CommonFieldsFilterset):
    """Filter facilities."""

    search = filters.SearchFilter()

    class Meta:
        """Set up filter options."""

        model = Facility
        fields = "__all__"


class SystemFilter(CommonFieldsFilterset):
    """Filter systems."""

    search = filters.SearchFilter()

    class Meta:
        """Set up filter options."""

        model = System
        fields = "__all__"


class FacilityUserFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:
        model = FacilityUser
        fields = (
            "facility",
            "user",
        )
