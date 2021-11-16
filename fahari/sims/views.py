from typing import Any, Dict, Optional, TypedDict, Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.base import ContextMixin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from fahari.common.views import ApprovedMixin, BaseFormMixin, BaseView, FormContextMixin

from .filters import QuestionAnswerFilter, QuestionGroupFilter, QuestionnaireResponsesFilter
from .forms import MentorshipTeamMemberForm, QuestionnaireResponsesForm
from .models import Question, QuestionAnswer, QuestionGroup, Questionnaire, QuestionnaireResponses
from .serializers import (
    QuestionAnswerSerializer,
    QuestionGroupSerializer,
    QuestionnaireResponsesSerializer,
)

# =============================================================================
# CONSTANTS
# =============================================================================


class QuestionAnswerPayload(TypedDict):
    comments: Optional[str]
    response: Optional[Union[bool, float, int, str]]


class QuestionGroupAnswersPayload(TypedDict):
    question_group: str  # The pk of the question group
    question_answers: Dict[str, QuestionAnswerPayload]  # The pk of the question being answered


# =============================================================================
# VIEWS
# =============================================================================


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


class QuestionAnswerViewSet(BaseView):
    queryset = QuestionAnswer.objects.active()
    serializer_class = QuestionAnswerSerializer
    filterset_class = QuestionAnswerFilter
    ordering = ("question__precedence",)
    search_fields = ("question_response__questionnaire", "question", "comments")


class QuestionGroupViewSet(BaseView):
    queryset = QuestionGroup.objects.active()
    serializer_class = QuestionGroupSerializer
    filterset_class = QuestionGroupFilter
    ordering = (
        "title",
        "precedence",
    )
    search_fields = ("title",)


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


class QuestionnaireResponseUpdateView(
    MentorShipQuestionnaireResponsesContextMixin, BaseFormMixin, FormContextMixin, UpdateView
):
    form_class = QuestionnaireResponsesForm
    model = QuestionnaireResponses
    # success_url = reverse_lazy("sims:questionnaire_responses")

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

    def get_success_url(self) -> str:
        return reverse_lazy(
            "sims:questionnaire_responses_capture", kwargs={"pk": self.get_object().pk}
        )


class QuestionnaireResponseViewSet(BaseView):
    queryset = QuestionnaireResponses.objects.active()
    serializer_class = QuestionnaireResponsesSerializer
    filterset_class = QuestionnaireResponsesFilter
    ordering_fields = ("facility_name",)
    search_fields = ("facility_name",)
    facility_field_lookup = "facility"

    @action(detail=True, methods=["POST"])
    def save_question_group_answers(self, request: Request, pk) -> Response:
        payload: QuestionGroupAnswersPayload = request.data
        print(payload)
        question_group: QuestionGroup
        try:
            question_group = QuestionGroup.objects.get(pk=payload["question_group"])
        except QuestionGroup.DoesNotExist:
            return Response(
                self._create_error_response_data(
                    'A question group with id "%s" does not exist.' % payload["question_group"]
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, data = self.perform_save_question_group_answers(
            question_group, payload["question_answers"]
        )
        return Response(
            data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
        )

    def perform_save_question_group_answers(
        self, question_group: QuestionGroup, data: Dict[str, QuestionAnswerPayload]
    ) -> (bool, Dict[str, Any]):
        if question_group.is_parent:
            return False, self._create_error_response_data(
                "The selected question group has no questions."
            )

        questionnaire_response: QuestionnaireResponses = self.get_object()
        for question_pk, question_answer in data.items():
            try:
                question = question_group.questions.get(pk=question_pk)  # noqa
            except Question.DoesNotExist:
                return False, self._create_error_response_data(
                    'A question with id "%s" does not exist.' % question_pk
                )

            question_answer_data = {
                "comments": question_answer.get("comments", ""),
                "created_by": self.request.user.pk,
                "response": {"content": question_answer.get("response")},
                "updated_by": self.request.user.pk,
            }
            QuestionAnswer.objects.update_or_create(
                organisation=question.organisation,
                question=question,
                questionnaire_response=questionnaire_response,
                defaults=question_answer_data,
            )

        return True, {"success": True}

    @staticmethod
    def _create_error_response_data(error_message: str) -> Dict[str, str]:
        return {"error_message": error_message, "success": False}


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
