from rest_framework import serializers

from fahari.common.serializers import BaseSerializer, FacilitySerializer, SystemSerializer

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
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    WeeklyProgramUpdateComment,
)


class CommoditySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Commodity
        fields = "__all__"


class FacilitySystemSerializer(BaseSerializer):

    facility_data = FacilitySerializer(source="facility", read_only=True)
    system_data = SystemSerializer(source="system", read_only=True)
    county = serializers.ReadOnlyField(source="facility.county")
    updated = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = FacilitySystem
        fields = "__all__"


class FacilitySystemTicketSerializer(BaseSerializer):

    facility_system_data = FacilitySystemSerializer(source="facility_system", read_only=True)
    facility_system_name = serializers.ReadOnlyField()
    is_open = serializers.ReadOnlyField()
    raised = serializers.DateTimeField(format="%d-%b-%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = FacilitySystemTicket
        fields = "__all__"


class StockReceiptVerificationSerializer(BaseSerializer):

    facility_data = FacilitySerializer(source="facility", read_only=True)
    commodity_data = CommoditySerializer(source="commodity", read_only=True)
    pack_size_name = serializers.SerializerMethodField()

    def get_pack_size_name(self, obj: StockReceiptVerification) -> str:  # noqa
        return obj.pack_size.name if obj.pack_size else "-"

    class Meta(BaseSerializer.Meta):
        model = StockReceiptVerification
        fields = "__all__"


class ActivityLogSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = ActivityLog
        fields = "__all__"


class DailyUpdateSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")

    class Meta(BaseSerializer.Meta):
        model = DailyUpdate
        fields = "__all__"


class TimeSheetSerializer(BaseSerializer):
    is_full_day = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    staff_name = serializers.ReadOnlyField(source="staff.name")
    approver = serializers.ReadOnlyField(source="approved_by.name")

    class Meta(BaseSerializer.Meta):
        model = TimeSheet
        fields = "__all__"


class WeeklyProgramUpdateSerializer(BaseSerializer):
    operation_area_display = serializers.ReadOnlyField(source="get_operation_area_display")
    status_display = serializers.ReadOnlyField(source="get_status_display")
    date = serializers.DateField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdate
        fields = "__all__"


class WeeklyProgramUpdateCommentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdateComment
        fields = "__all__"


class WeeklyProgramUpdateCommentsReadSerializer(BaseSerializer):
    weekly_update = WeeklyProgramUpdateSerializer()
    date_created = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdateComment
        fields = "__all__"


class UoMCategorySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = UoMCategory
        fields = "__all__"


class UoMSerializer(BaseSerializer):
    category_data = UoMCategorySerializer(source="category", read_only=True)

    class Meta(BaseSerializer.Meta):
        model = UoM
        fields = "__all__"


class FacilityNetworkStatusSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")

    class Meta(BaseSerializer.Meta):
        model = FacilityNetworkStatus
        fields = "__all__"


class FacilityDeviceSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")

    class Meta(BaseSerializer.Meta):
        model = FacilityDevice
        fields = "__all__"


class FacilityDeviceRequestSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")

    class Meta(BaseSerializer.Meta):
        model = FacilityDeviceRequest
        fields = "__all__"


class SecurityIncidenceSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")

    class Meta(BaseSerializer.Meta):
        model = SecurityIncidence
        fields = "__all__"
