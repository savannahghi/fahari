import pytest
from faker import Faker
from model_bakery import baker
from rest_framework.test import APITestCase

from fahari.common.models import Facility, Organisation
from fahari.common.tests.test_api import LoggedInMixin
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


class InitializeTestData(LoggedInMixin, APITestCase):
    def setUp(self):
        organisation = baker.make(Organisation)
        facility = baker.make(Facility, organisation=organisation, name=fake.text(max_nb_chars=30))
        self.questionnaire = baker.make(
            Questionnaire, name=fake.text(max_nb_chars=30), questionnaire_type="mentorship"
        )
        self.question_response = baker.make(
            QuestionnaireResponses, facility=facility, questionnaire=self.questionnaire
        )
        self.question_group = baker.make(
            QuestionGroup,
            title=fake.text(max_nb_chars=30),
            questionnaire=self.questionnaire,
            precedence=1,
        )
        super().setUp()

    def test_question_queryset(self):
        question = baker.make(Question, query="What's your name?", answer_type="yes_no")
        assert (question.is_answerable) is True
        # assert(question.is_answered_for_questionnaire(question_response)) is True

    def test_questiongroup_is_complete_for_questionnaire(self):
        pass
        # assert self.question_group.is_complete_for_questionnaire(self.question_response) is True
