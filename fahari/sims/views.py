from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView, FormContextMixin

from .filters import QuestionnaireResponsesFilter
from .forms import MentorshipTeamMemberForm, QuestionnaireResponsesForm
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


class QuestionnaireResponsesCaptureView(QuestionnaireResponsesContextMixin, DetailView):
    model = QuestionnaireResponses
    template_name = "pages/sims/questionnaire_responses_capture.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_step"] = 2
        context["questionnaire"] = self.get_object().questionnaire  # noqa
        context["total_steps"] = 2

        return context


class QuestionnaireResponseCreateView(
    QuestionnaireResponsesContextMixin, BaseFormMixin, FormContextMixin, CreateView
):
    form_class = QuestionnaireResponsesForm
    model = QuestionnaireResponses
    success_url = reverse_lazy("sims:questionnaire_responses")

    def form_valid(self, form):
        form.instance.metadata["mentors"] = form.cleaned_data["mentors"]
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


class QuestionnaireResponseUpdateView(
    MentorShipQuestionnaireResponsesContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = QuestionnaireResponsesForm
    model = QuestionnaireResponses
    success_url = reverse_lazy("sims:questionnaire_responses")

    def form_valid(self, form):
        form.instance.metadata["mentors"] = form.cleaned_data["mentors"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["current_step"] = 1
        context["mentor_details_form"] = MentorshipTeamMemberForm()
        context["questionnaire"] = self.get_object().questionnaire  # noqa
        context["total_steps"] = 2

        return context

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["mentors"] = self.get_object().metadata.get("mentors", [])  # noqa
        return initial


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
