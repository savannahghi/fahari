from rest_framework import filters

from ..models import Facility, System, UserFacilityAllotment
from .base_filters import CommonFieldsFilterset


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


class UserFacilityAllotmentFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:
        model = UserFacilityAllotment
        fields = ("user",)
