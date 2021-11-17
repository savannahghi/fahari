from typing import Optional

from django import template

from ..models import Question, QuestionAnswer, QuestionnaireResponses

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
