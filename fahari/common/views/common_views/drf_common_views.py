from fahari.common.dashboard import get_fahari_facilities_queryset
from fahari.common.filters import FacilityFilter, SystemFilter, UserFacilityAllotmentFilter
from fahari.common.models import System, UserFacilityAllotment
from fahari.common.serializers import (
    FacilitySerializer,
    SystemSerializer,
    UserFacilityAllotmentSerializer,
)

from ..base_views import BaseView


class FacilityViewSet(BaseView):
    queryset = get_fahari_facilities_queryset()
    serializer_class = FacilitySerializer
    filterset_class = FacilityFilter
    ordering_fields = ("name", "mfl_code", "county", "sub_county", "ward")
    search_fields = (
        "name",
        "mfl_code",
        "registration_number",
    )
    facility_field_lookup = "pk"


class SystemViewSet(BaseView):
    queryset = System.objects.active()
    serializer_class = SystemSerializer
    filterset_class = SystemFilter
    ordering_fields = ("name",)
    search_fields = ("name",)


class UserFacilityViewSet(BaseView):
    queryset = UserFacilityAllotment.objects.active().order_by(
        "user__name", "user__username", "-updated", "-created"
    )
    serializer_class = UserFacilityAllotmentSerializer
    filterset_class = UserFacilityAllotmentFilter
    ordering_fields = ("user__name", "user__username", "allotment_type")
    search_fields = ("allotment_type", "user__name", "user__username")
