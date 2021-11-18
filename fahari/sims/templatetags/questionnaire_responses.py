from typing import Optional

from django import template

from ..models import Question, QuestionAnswer, QuestionGroup, QuestionnaireResponses

register = template.Library()


@register.filter
def answer_for_questionnaire(
    value: Question, responses: QuestionnaireResponses
) -> Optional[QuestionAnswer]:
    """Return the answer to the given question for the provided questionnaire responses."""

    return value.answer_for_questionnaire(responses)


@register.filter
def is_answered_for_questionnaire(value: Question, responses: QuestionnaireResponses) -> bool:
    """Return true if the given question has been answered for the given questionnaire responses.


    If the given question is a parent question, true will only be returned if
    all it's sub-questions have also being answered.
    """

    return value.is_answered_for_questionnaire(responses)


@register.filter
def is_complete_for_questionnaire(value: QuestionGroup, responses: QuestionnaireResponses) -> bool:
    """Return true if the given question group has been fully answered for the provided responses.

    This will only return true if all the questions and sub-questions of the
    given question group have answers for the provided questionnaire responses.
    """

    return value.is_complete_for_questionnaire(responses)


@register.filter
def is_not_applicable_for_questionnaire(
    value: QuestionGroup, responses: QuestionnaireResponses
) -> bool:
    """Returns true if the given group's questions are not answerable for the given responses.

    That is, for all the questions in the given question group, only not
    applicable answers have been provided for the provided questionnaire
    response.
    """
    return value.is_not_applicable_for_questionnaire(responses)
