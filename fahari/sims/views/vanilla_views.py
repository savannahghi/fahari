from typing import Any, Dict, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from fahari.common.views import ApprovedMixin, BaseFormMixin, FormContextMixin

from ..forms import MentorshipTeamMemberForm, QuestionnaireResponsesForm
from ..models import Questionnaire, QuestionnaireResponses


class QuestionnaireResponsesContextMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["active"] = "sims-nav"  # id of active nav element
        context["selected"] = "questionnaire-responses"  # id of selected page

        return context


class QuestionnaireResponsesView(
    QuestionnaireResponsesContextMixin, LoginRequiredMixin, ApprovedMixin, TemplateView
):
    permission_required = "sims.view_questionnaireresponses"
    template_name = "pages/sims/questionnaire_responses.html"


class QuestionnaireResponsesCaptureView(QuestionnaireResponsesContextMixin, DetailView):
    model = QuestionnaireResponses
    template_name = "pages/sims/questionnaire_responses_capture.html"

    def get_context_data(self, **kwargs):
        responses: QuestionnaireResponses = self.get_object()  # type: ignore
        questionnaire_obj: QuestionnaireResponses = responses.questionnaire  # type: ignore
        context = super().get_context_data(**kwargs)
        context["current_step"] = 2
        context["questionnaire"] = questionnaire_obj
        context["questionnaire_is_complete"] = responses.is_complete
        context["total_steps"] = 2

        return context


class QuestionnaireResponsesCreateView(
    QuestionnaireResponsesContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = QuestionnaireResponsesForm
    model = QuestionnaireResponses
    success_url = reverse_lazy("sims:questionnaire_responses")

    # Protected properties
    _questionnaire: Optional[Questionnaire] = None

    def form_valid(self, form):
        form.instance.metadata["mentors"] = form.cleaned_data["mentors"]
        self._questionnaire = form.instance
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_step"] = 1
        context["mentor_details_form"] = MentorshipTeamMemberForm()
        context["questionnaire"] = self.get_object(Questionnaire.objects.active())
        context["total_steps"] = 2

        return context

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["questionnaire"] = self.get_object(Questionnaire.objects.active())
        return initial

    def get_success_url(self) -> str:
        return (
            reverse_lazy(
                "sims:questionnaire_responses_capture", kwargs={"pk": self._questionnaire.pk}
            )
            if self._questionnaire
            else self.success_url
        )


class QuestionnaireResponsesUpdateView(
    QuestionnaireResponsesContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = QuestionnaireResponsesForm
    model = QuestionnaireResponses

    def form_valid(self, form):
        form.instance.metadata["mentors"] = form.cleaned_data["mentors"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_step"] = 1
        context["mentor_details_form"] = MentorshipTeamMemberForm()
        context["questionnaire"] = self.get_object().questionnaire  # type: ignore
        context["total_steps"] = 2

        return context

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["mentors"] = self.get_object().metadata.get("mentors", [])  # type: ignore
        return initial

    def get_success_url(self) -> str:
        return reverse_lazy(
            "sims:questionnaire_responses_capture", kwargs={"pk": self.get_object().pk}
        )


class QuestionnaireSelectionView(LoginRequiredMixin, ApprovedMixin, TemplateView):
    permission_required = "sims.view_questionnaire"
    template_name = "pages/sims/questionnaire_selection.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["questionnaires"] = Questionnaire.objects.active()

        return context
