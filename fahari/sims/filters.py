import django_filters
from rest_framework import filters

from fahari.common.filters import CommonFieldsFilterset

from .models import QuestionAnswer, QuestionGroup, QuestionnaireResponses


class QuestionAnswerFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:
        model = QuestionAnswer
        fields = ("question", "answered_on", "comments")


class QuestionGroupFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    class Meta:
        model = QuestionGroup
        fields = ("title", "precedence")


class QuestionnaireResponsesFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    def get_by_complete_status(self, queryset, field, value: bool):  # noqa
        if value:
            return queryset.none()
        return queryset

    is_complete = django_filters.BooleanFilter(method="get_by_complete_status")

    class Meta:
        model = QuestionnaireResponses
        fields = ("facility", "questionnaire", "start_date", "finish_date", "is_complete")
