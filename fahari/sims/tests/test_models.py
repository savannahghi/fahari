import pytest
from faker import Faker
from model_bakery import baker

from fahari.sims.models import (
    Question,
    QuestionAnswer,
    QuestionGroup,
    Questionnaire,
    QuestionnaireResponses,
)

fake = Faker()
pytestmark = pytest.mark.django_db


def test_string_reprs():
    models = [
        Question,
        QuestionGroup,
        Questionnaire,
        QuestionAnswer,
        QuestionnaireResponses,
    ]
    for model in models:
        instance = baker.prepare(model)
        assert str(instance) != ""


def test_question_queryset():
    question = baker.make(Question, query="What's your name?", answer_type="yes_no")
    assert (question.is_answerable) is True
