from rest_framework import filters

from fahari.common.filters import CommonFieldsFilterset

from .models import (
    ActivityLog,
    Commodity,
    DailyUpdate,
    FacilitySystem,
    FacilitySystemTicket,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
)


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
        fields = ("date",)


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
