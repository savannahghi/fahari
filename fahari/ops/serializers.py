from rest_framework import serializers

from fahari.common.serializers import BaseSerializer

from .models import (
    ActivityLog,
    Checklist,
    Commodity,
    DailyUpdate,
    FacilityDevice,
    FacilityDeviceRequest,
    FacilityNetworkStatus,
    FacilitySystem,
    FacilitySystemTicket,
    MentorshipChecklist,
    Question,
    QuestionAnswer,
    SecurityIncidence,
    SiteMentorship,
    StockReceiptVerification,
    TimeSheet,
    UoM,
    UoMCategory,
    WeeklyProgramUpdate,
    WeeklyProgramUpdateComment,
)


class FacilitySystemSerializer(BaseSerializer):

    facility_name = serializers.ReadOnlyField()
    system_name = serializers.ReadOnlyField()
    county = serializers.ReadOnlyField(source="facility.county")
    updated = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = FacilitySystem
        fields = "__all__"


class FacilitySystemTicketSerializer(BaseSerializer):

    facility_system_name = serializers.ReadOnlyField()
    is_open = serializers.ReadOnlyField()
    raised = serializers.DateTimeField(format="%d-%b-%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = FacilitySystemTicket
        fields = "__all__"


class StockReceiptVerificationSerializer(BaseSerializer):

    facility_name = serializers.ReadOnlyField(source="facility.name")
    commodity_name = serializers.ReadOnlyField(source="commodity.name")
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


class SiteMentorshipSerializer(BaseSerializer):
    staff_member_name = serializers.ReadOnlyField(source="staff_member.name")
    site_name = serializers.ReadOnlyField(source="site.name")

    class Meta(BaseSerializer.Meta):
        model = SiteMentorship
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
    facility_name = serializers.ReadOnlyField(source="facility.name")
    date_created = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdate
        fields = "__all__"


class WeeklyProgramUpdateCommentSerializer(BaseSerializer):
    date_created = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdateComment
        fields = "__all__"


class WeeklyProgramUpdateCommentsReadSerializer(BaseSerializer):
    weekly_update = WeeklyProgramUpdateSerializer()
    date_created = serializers.DateTimeField(format="%d/%m/%Y", required=False)

    class Meta(BaseSerializer.Meta):
        model = WeeklyProgramUpdateComment
        fields = "__all__"


class CommoditySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Commodity
        fields = "__all__"


class UoMSerializer(BaseSerializer):

    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta(BaseSerializer.Meta):
        model = UoM
        fields = "__all__"


class UoMCategorySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = UoMCategory
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


class QuestionSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Question
        fields = "__all__"


class QuestionAnswerSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")
    question = serializers.ReadOnlyField(source="question.question")

    class Meta(BaseSerializer.Meta):
        model = QuestionAnswer
        fields = "__all__"


class ChecklistSerializer(BaseSerializer):
    questions = QuestionSerializer(many=True)

    class Meta(BaseSerializer.Meta):
        model = Checklist
        fields = "__all__"


class MentorshipChecklistSerializer(BaseSerializer):
    facility_name = serializers.ReadOnlyField(source="facility.name")
    mentor = serializers.ReadOnlyField(source="mentor.email")
    checklist = ChecklistSerializer(many=True)

    class Meta(BaseSerializer.Meta):
        model = MentorshipChecklist
        fields = "__all__"
