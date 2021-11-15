from rest_framework import filters

from fahari.common.filters import CommonFieldsFilterset

from .models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    WeeklyProgramUpdateComment,
)


class FacilitySystemFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilitySystem
        exclude = (
            "attachment",
            "trainees",
        )


class FacilitySystemTicketFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilitySystemTicket
        fields = "__all__"


class StockReceiptVerificationFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = StockReceiptVerification
        exclude = ("delivery_note_image",)


class ActivityLogFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = ActivityLog
        fields = "__all__"


class SiteMentorshipFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = SiteMentorship
        fields = "__all__"


class DailyUpdateFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = DailyUpdate
        fields = "__all__"


class TimeSheetFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = TimeSheet
        fields = "__all__"


class WeeklyProgramUpdateFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = WeeklyProgramUpdate
        exclude = (
            "attachment",
            "assigned_persons",
        )


class WeeklyProgramUpdateCommentsFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = WeeklyProgramUpdateComment
        fields = "__all__"


class CommodityFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = Commodity
        fields = (
            "name",
            "code",
            "description",
        )


class UoMFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = UoM
        fields = "__all__"


class UoMCategoryFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = UoMCategory
        fields = "__all__"


class FacilityNetworkStatusFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilityNetworkStatus
        fields = "__all__"


class FacilityDeviceFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilityDevice
        fields = "__all__"


class FacilityDeviceRequestFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = FacilityDeviceRequest
        fields = "__all__"


class SecurityIncidenceFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = SecurityIncidence
        fields = "__all__"
