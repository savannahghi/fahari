from typing import Any, Dict

# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin

from fahari.common.views import ApprovedMixin, BaseView

from .filters import QuestionnaireResponsesFilter
from .models import Questionnaire, QuestionnaireResponses
from .serializers import QuestionnaireResponsesSerializer


class QuestionnaireResponsesContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["active"] = "sims-nav"  # id of active nav element
        context["selected"] = "questionnaire-responses"  # id of selected page

        return context


class MentorShipQuestionnaireResponsesContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context


class QuestionnaireResponsesView(
    QuestionnaireResponsesContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    permission_required = "sims.view_questionnaireresponses"
    template_name = "pages/sims/questionnaire_responses.html"


class QuestionnaireResponseViewSet(BaseView):
    queryset = QuestionnaireResponses.objects.active()
    serializer_class = QuestionnaireResponsesSerializer
    filterset_class = QuestionnaireResponsesFilter
    ordering_fields = ("facility_name",)
    search_fields = ("facility_name",)
    facility_field_lookup = "facility"


class QuestionnaireSelectionView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    permission_required = "sims.view_questionnaire"
    template_name = "pages/sims/questionnaire_selection.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["questionnaires"] = Questionnaire.objects.active()

        return context


class MentorshipQuestionnaireResponsesView(
    QuestionnaireResponsesView, MentorShipQuestionnaireResponsesContextMixin
):
    ...
