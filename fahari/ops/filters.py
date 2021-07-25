from rest_framework import filters

from fahari.common.filters import CommonFieldsFilterset

from .models import FacilitySystem, FacilitySystemTicket


class FacilitySystemFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilitySystem
        fields = "__all__"


class FacilitySystemTicketFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilitySystemTicket
        fields = "__all__"
