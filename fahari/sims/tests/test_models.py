import pytest
from django.contrib.gis.db import models
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
    get_metadata_processors_for_metadata_option,
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
        self.facility = baker.make(
            Facility, organisation=organisation, name=fake.text(max_nb_chars=30)
        )
        self.questionnaire = baker.make(
            Questionnaire, name=fake.text(max_nb_chars=30), questionnaire_type="mentorship"
        )
        self.questionnaire_response = baker.make(
            QuestionnaireResponses,
            facility=self.facility,
            questionnaire=self.questionnaire,
        )
        self.question_group = baker.make(
            QuestionGroup,
            title=fake.text(max_nb_chars=30),
            questionnaire=self.questionnaire,
            precedence=1,
        )
        self.metadata = {
            "contraints": {"min_value": 0, "max_value": 10},
            "select_list_options": ["ARV", "CD", "DCD", "Femiplan"],
        }
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
            answer_type="real",
            question_group=self.question_group,
            precedence=1,
            metadata=self.metadata,
        )
        self.parent_qn = baker.make(
            Question,
            parent=None,
            query="Soe test qn.?",
            answer_type="real",
            precedence=1,
            metadata={},
        )

        self.question = baker.make(
            Question,
            parent=self.qn_2,
            query="What number makes up female?",
            answer_type="real",
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
        self.answered_count = self.questionnaire_response.answers.filter(  # noqa
            models.Q(is_not_applicable=True) | ~models.Q(response__content=None)
        ).count()
        self.question_qs = Question.objects.all()
        self.question_group_qs = QuestionGroup.objects.all()
        self.questionnaire_response_qs = QuestionnaireResponses.objects.all()
        super().setUp()

    get_metadata_processors_for_metadata_option("depends_on", None)

    def test_is_complete_for_questionnaire(self):

        assert (
            self.question_group.is_complete_for_questionnaire(self.questionnaire_response) is False
        )

    def test_is_not_applicable_for_questionnaire(self):
        assert (
            self.question_group.is_not_applicable_for_questionnaire(self.questionnaire_response)
            is False
        )

    def test_is_valid(self):
        assert self.question_answer.is_valid is False

    def test_progress(self):
        assert self.questionnaire_response.progress == (self.answered_count / self.total_questions)

    def test_questionnaire_response_url(self):
        url = self.questionnaire_response.get_absolute_url()
        assert f"/sims/questionnaire_responses_update/{self.questionnaire_response.pk}" in url

    def test_methods(self):
        self.question.answer_for_questionnaire(self.questionnaire_response)
        self.qn_1.is_answered_for_questionnaire(self.questionnaire_response)
        self.parent_qn.is_answered_for_questionnaire(self.questionnaire_response)
        assert (
            self.question_group.is_not_applicable_for_questionnaire(self.questionnaire_response)
            is False
        )

    def test_metadata_processing(self):
        self.qn_2.save()

    def test_properties(self):
        self.question.children
        assert self.qn_1.is_parent is True
        assert self.question.is_answerable is True
        self.question_group.direct_decedents_only
        self.questionnaire.direct_decedents_only
        self.questionnaire_response.is_complete

    def test_queryset(self):
        self.question_qs.answered_for_questionnaire(self.questionnaire_response)
        self.question_qs.answerable()
        self.question_qs.for_question(self.question)
        self.question_qs.for_question_group(self.question_group)
        self.question_group_qs.for_questionnaire(self.questionnaire)
        self.question_group_qs.parents_only()
        self.question_group_qs.answered_for_questionnaire(self.questionnaire_response)
        self.questionnaire_response_qs.draft()
        self.questionnaire_response_qs.complete()

    def test_managers(self):
        Question.objects.answerable()
        Question.objects.by_precedence()
        Question.objects.for_question(self.question)
        Question.objects.for_question_group(self.question_group)
        Question.objects.answered_for_questionnaire(self.questionnaire_response)
        QuestionGroup.objects.by_precedence()
        QuestionGroup.objects.for_questionnaire(self.questionnaire)
        QuestionGroup.objects.answered_for_questionnaire(self.questionnaire_response)
        QuestionnaireResponses.objects.draft()
        QuestionnaireResponses.objects.complete()
