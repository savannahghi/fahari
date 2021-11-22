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
        self.questionnaire_response = baker.make(
            QuestionnaireResponses,
            facility=facility,
            questionnaire=self.questionnaire,
        )
        self.question_group = baker.make(
            QuestionGroup,
            title=fake.text(max_nb_chars=30),
            questionnaire=self.questionnaire,
            precedence=1,
        )

        self.qn_1 = baker.make(
            Question,
            query="Based on last month's result",
            answer_type="none",
            question_group=self.question_group,
            precedence=1,
            metadata={},
        )

        self.qn_2 = baker.make(
            Question,
            parent=self.qn_1,
            query="How many people were diagnosed positive?",
            answer_type="number",
            question_group=self.question_group,
            precedence=1,
            metadata={},
        )

        self.question = baker.make(
            Question,
            parent=self.qn_2,
            query="What number makes up female?",
            answer_type="number",
            question_group=self.question_group,
            precedence=1,
            metadata={},
        )
        self.question_answer = baker.make(
            QuestionAnswer,
            organisation=organisation,
            questionnaire_response=self.questionnaire_response,
            question=self.question,
            is_not_applicable=False,
            response={"response": 5, "comments": "some response"},
        )
        self.total_questions = Question.objects.for_questionnaire(self.questionnaire).count()
        self.answered_count = self.questionnaire_response.answers.count()
        super().setUp()

    def test_is_complete_for_questionnaire(self):

        assert (
            self.question_group.is_complete_for_questionnaire(self.questionnaire_response) is True
        )

    def test_is_not_applicable_for_questionnaire(self):
        assert (
            self.question_group.is_not_applicable_for_questionnaire(self.questionnaire_response)
            is True
        )

    def test_is_valid(self):
        assert self.question_answer.is_valid is True

    def test_progress(self):
        assert self.questionnaire_response.progress == (self.answered_count / self.total_questions)

    def test_questionnaire_response_url(self):
        url = self.questionnaire_response.get_absolute_url()
        assert f"/sims/questionnaire_responses_update/{self.questionnaire_response.pk}" in url

    def test_methods(self):
        self.question.answer_for_questionnaire(self.questionnaire_response)
        assert self.qn_1.is_answered_for_questionnaire(self.questionnaire_response) is False
        assert self.qn_2.is_answered_for_questionnaire(self.questionnaire_response) is True
        assert (
            self.question_group.is_not_applicable_for_questionnaire(self.questionnaire_response)
            is True
        )

    def test_properties(self):
        self.question.children
        assert self.qn_1.is_parent is True
        assert self.question.is_answerable is True
        self.question_group.direct_decedents_only
        self.questionnaire.direct_decedents_only

    def test_queryset(self):
        Question.objects.all().answerable()
        Question.objects.all().answered_for_questionnaire(self.questionnaire_response)
        Question.objects.all().for_question(self.question)
        Question.objects.all().for_question_group(self.question_group)
        QuestionGroup.objects.all().for_questionnaire(self.questionnaire)
        QuestionGroup.objects.all().parents_only()

    def test_managers(self):
        Question.objects.answerable()
        Question.objects.by_precedence()
        Question.objects.for_question(self.question)
        Question.objects.for_question_group(self.question_group)
        Question.objects.answered_for_questionnaire(self.questionnaire_response)
        QuestionGroup.objects.by_precedence()
        QuestionGroup.objects.for_questionnaire(self.questionnaire)
