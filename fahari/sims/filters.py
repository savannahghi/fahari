import django_filters
from rest_framework import filters

from fahari.common.filters import CommonFieldsFilterset

from .models import QuestionnaireResponses


class QuestionnaireResponsesFilter(CommonFieldsFilterset):

    search = filters.SearchFilter()

    def get_by_complete_status(self, queryset, field, value):  # noqa
        return queryset

    is_complete = django_filters.BooleanFilter(method="get_by_complete_status")

    class Meta:
        model = QuestionnaireResponses
        fields = ("facility", "questionnaire", "start_date", "finish_date", "is_complete")
