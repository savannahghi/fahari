from rest_framework import filters

from ..models import UserFacilityAllotment


class AllottedFacilitiesFilterBackend(filters.BaseFilterBackend):
    """Users are only allowed to view records relating to facilities they have been allotted to.

    For this to work, the attribute `facility_field_lookup` must be present on a view. The
    attribute should contain a lookup to a facility and should be usable from the queryset
    returned by the view. If the aforementioned attribute is not present on a view, then no
    filtering is performed and the queryset is returned as is.
    """

    def filter_queryset(self, request, queryset, view):
        """Exclude records associated to facilities that the requesting user is not allotted."""
        lookup = getattr(view, "facility_field_lookup", None)
        if not lookup:
            return queryset
        allotted_facilities = UserFacilityAllotment.get_facilities_for_user(request.user)
        qs_filter = {"%s__in" % lookup: allotted_facilities}
        return queryset.filter(**qs_filter)


class OrganisationFilterBackend(filters.BaseFilterBackend):
    """Users are only allowed to view records in their organisation."""

    def filter_queryset(self, request, queryset, view):
        """Filter all records that have an organisation field by user org."""
        return queryset.filter(organisation=request.user.organisation)
