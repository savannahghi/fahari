from typing import Any, Dict

# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin

from fahari.common.views import ApprovedMixin


class QuestionnaireResponsesContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context


class MentorShipQuestionnaireResponsesContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context


class QuestionnaireResponsesView(
    QuestionnaireResponsesContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    permission_required = "sims.view_questionnaireresponses"


class MentorshipQuestionnaireResponsesView(
    QuestionnaireResponsesView, MentorShipQuestionnaireResponsesContextMixin
):
    ...
