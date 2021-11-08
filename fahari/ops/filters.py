import django_filters
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
    MentorshipQuestionnaire,
    MentorshipTeamMember,
    Question,
    QuestionGroup,
    Questionnaire,
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


class QuestionFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = Question
        exclude = ("metadata",)


class QuestionGroupFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = QuestionGroup
        fields = "__all__"


class QuestionnaireFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:

        model = Questionnaire
        fields = "__all__"


class MentorshipTeamMemberFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    def get_team_by_qnaire_id(self, queryset, field, value):  # noqa
        print("seee ", value)
        team_ids = MentorshipQuestionnaire.objects.filter(pk=value).values_list(
            "mentorship_team", flat=True
        )

        return queryset.filter(pk__in=team_ids)

    is_qn_team = django_filters.CharFilter(method="get_team_by_qnaire_id")

    class Meta:

        model = MentorshipTeamMember
        fields = "__all__"


class MentorshipQuestionnaireFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    def get_by_complete_status(self, queryset, field, value):  # noqa
        questionnaires = map(
            lambda q: q.pk,
            filter(lambda q: q.is_complete if value else not q.is_complete, queryset),
        )
        return queryset.filter(pk__in=questionnaires)

    is_complete = django_filters.BooleanFilter(method="get_by_complete_status")

    class Meta:

        model = MentorshipQuestionnaire
        fields = "__all__"
