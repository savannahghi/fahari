from typing import Any, Dict, List, Optional, Sequence, Tuple, TypedDict, Union

from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from fahari.common.views import BaseView

from ..filters import QuestionnaireResponsesFilter
from ..models import Question, QuestionAnswer, QuestionGroup, QuestionnaireResponses
from ..serializers import (
    QuestionAnswerSerializer,
    QuestionGroupSerializer,
    QuestionnaireResponsesSerializer,
)
from .answer_value_conversions_utils import DEFAULT_ANSWER_VALUE_CONVERTERS

# =============================================================================
# CONSTANTS
# =============================================================================


class QuestionAnswerPayload(TypedDict):
    comments: Optional[str]
    response: Optional[Union[Any, Dict[str, Any], Sequence[Any]]]


class QuestionGroupAnswersPayload(TypedDict):
    question_group: str  # The pk of the question group
    question_answers: Dict[str, QuestionAnswerPayload]  # The pk of the question being answered


class QuestionGroupOperationsPayload(TypedDict):
    question_group: str  # The pk of the question group


# =============================================================================
# VIEWSETS
# =============================================================================


class QuestionnaireResponsesViewSet(BaseView):
    queryset = QuestionnaireResponses.objects.active()
    serializer_class = QuestionnaireResponsesSerializer
    filterset_class = QuestionnaireResponsesFilter
    ordering_fields = ("facility_name",)
    search_fields = ("facility_name",)
    facility_field_lookup = "facility"

    @action(detail=True, methods=["POST"])
    def mark_question_group_as_applicable(self, request: Request, pk) -> Response:
        """Mark question group as applicable."""

        payload: QuestionGroupOperationsPayload = request.data
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

        success, data = self.perform_mark_question_group_as_applicable(question_group)
        return Response(
            data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["POST"])
    def mark_question_group_as_non_applicable(self, request: Request, pk) -> Response:
        """Mark question group as non-applicable."""

        payload: QuestionGroupOperationsPayload = request.data
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

        success, data = self.perform_mark_question_group_as_non_applicable(question_group)
        return Response(
            data, status=status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["POST"])
    def save_question_group_answers(self, request: Request, pk) -> Response:
        """Save question group answers."""

        payload: QuestionGroupAnswersPayload = request.data
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

    @action(detail=True, methods=["POST"])
    def submit_questionnaire_responses(self, request: Request, pk):
        """Submit questionnaire responses."""

        self.perform_submit_questionnaire_responses()
        return HttpResponseRedirect(redirect_to=reverse_lazy("sims:questionnaire_responses"))

    def perform_mark_question_group_as_applicable(
        self, question_group: QuestionGroup
    ) -> Tuple[bool, Dict[str, Any]]:
        questionnaire_response: QuestionnaireResponses = self.get_object()

        response_data: Dict[str, Any] = {"answers": {}, "errors": {}}
        question_answer_data = {
            "created_by": self.request.user.pk,
            "is_not_applicable": False,
            "response": {"content": None},
            "updated_by": self.request.user.pk,
        }
        for question in Question.objects.for_question_group(question_group):
            self._save_question_answer(
                question, questionnaire_response, question_answer_data, response_data, True, True
            )

        question_group.refresh_from_db()
        self._update_response_data_with_question_group_details(
            response_data, question_group, questionnaire_response
        )
        response_data["success"] = True
        return True, response_data

    def perform_mark_question_group_as_non_applicable(
        self, question_group: QuestionGroup
    ) -> Tuple[bool, Dict[str, Any]]:
        questionnaire_response: QuestionnaireResponses = self.get_object()

        response_data: Dict[str, Any] = {"answers": {}, "errors": {}}
        question_answer_data = {
            "created_by": self.request.user.pk,
            "is_not_applicable": True,
            "response": {"content": None},
            "updated_by": self.request.user.pk,
        }
        for question in Question.objects.for_question_group(question_group):
            self._save_question_answer(
                question, questionnaire_response, question_answer_data, response_data, True
            )

        question_group.refresh_from_db()
        self._update_response_data_with_question_group_details(
            response_data, question_group, questionnaire_response
        )
        response_data["success"] = True
        return True, response_data

    def perform_save_question_group_answers(
        self, question_group: QuestionGroup, data: Dict[str, QuestionAnswerPayload]
    ) -> Tuple[bool, Dict[str, Any]]:
        if question_group.is_parent:
            return False, self._create_error_response_data(
                "The selected question group has no questions."
            )

        questionnaire_response: QuestionnaireResponses = self.get_object()
        response_data: Dict[str, Any] = {"answers": {}, "errors": {}}
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
            self._save_question_answer(
                question, questionnaire_response, question_answer_data, response_data
            )

        question_group.refresh_from_db()
        self._update_response_data_with_question_group_details(
            response_data, question_group, questionnaire_response
        )
        response_data["success"] = True
        return True, response_data

    def perform_submit_questionnaire_responses(self) -> Tuple[bool, Dict[str, Any]]:
        questionnaire_response: QuestionnaireResponses = self.get_object()
        question_answer_data = {
            "created_by": self.request.user.pk,
            "comments": "Skipped during submission.",
            "is_not_applicable": True,
            "response": {"content": None},
            "updated_by": self.request.user.pk,
        }
        for question in questionnaire_response.questions.exclude(
            pk__in=questionnaire_response.answered_questions.all()
        ):
            QuestionAnswer.objects.update_or_create(
                organisation=question.organisation,
                question=question,
                questionnaire_response=questionnaire_response,
                defaults=question_answer_data,
            )

        questionnaire_response.finish_date = timezone.now()
        questionnaire_response.save()

        return True, {"success": True}

    @staticmethod
    def _create_error_response_data(error_message: str) -> Dict[str, Any]:
        return {"error_message": error_message, "success": False}

    @staticmethod
    def _save_question_answer(
        question: Question,
        questionnaire_response: QuestionnaireResponses,
        question_answer_data: Dict[str, Any],
        response_data: Dict[str, Any],
        skip_conversion: bool = False,
        skip_metadata_processors_run: bool = False,
    ) -> None:
        question_pk = str(question.pk)
        try:
            cls = QuestionnaireResponsesViewSet
            if not skip_conversion:
                question_answer_data["response"]["content"] = cls._to_valid_answer(
                    question, question_answer_data["response"]["content"]
                )
            answer, created = QuestionAnswer.objects.update_or_create(
                organisation=question.organisation,
                question=question,
                questionnaire_response=questionnaire_response,
                defaults=question_answer_data,
            )
            response_data["answers"][question_pk] = {
                "created": created,
                "data": QuestionAnswerSerializer(answer).data,
            }

            # Run the answer's metadata processors
            if not skip_metadata_processors_run:
                answer.run()
        except ValidationError as exp:
            question_errors: List[str] = response_data["errors"].get(question_pk, [])
            question_errors.extend(exp.messages)
            response_data["errors"][question_pk] = question_errors

    @staticmethod
    def _to_valid_answer(question: Question, answer_value: Any) -> Any:
        answer_convertor = DEFAULT_ANSWER_VALUE_CONVERTERS.get(question.answer_type)
        if not answer_convertor:
            raise ValidationError('Unsupported question type "%s".' % question.answer_type)

        return answer_convertor.to_python(answer_value)

    @staticmethod
    def _update_response_data_with_question_group_details(
        response_data: Dict[str, Any],
        question_group: QuestionGroup,
        questionnaire_response: QuestionnaireResponses,
    ) -> None:
        response_data["question_group"] = QuestionGroupSerializer(question_group).data
        response_data["question_group"]["is_complete"] = question_group.is_complete_for_responses(
            questionnaire_response
        )
