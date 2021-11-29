import pytest
from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from faker import Faker
from model_bakery import baker
from rest_framework.test import APITestCase

from fahari.common.models import Facility, Organisation
from fahari.common.tests.test_api import LoggedInMixin
from fahari.sims.models import (
    ChildrenMixin,
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


class QuestionTest(TestCase):
    """Tests for the Question model."""

    def setUp(self) -> None:
        self.organisation = baker.make(Organisation)
        self.facility = baker.make(
            Facility,
            county="Kajiado",
            organisation=self.organisation,
            sub_county="Kajiado East",
        )
        self.questionnaire = baker.make(
            Questionnaire,
            name="Test Questionnaire 1",
            organisation=self.organisation,
            questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
        )
        self.question_group1 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 1",
        )
        self.question1 = baker.make(
            Question,
            answer_type=Question.AnswerType.YES_NO.value,
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=None,
            query=(
                "Evidence of quality management structure at facility level "
                "and leadership stewardship of the same?"
            ),
            question_code="1234",
            question_group=self.question_group1,
        )
        self.question2 = baker.make(
            Question,
            answer_type=Question.AnswerType.NONE.value,
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=(
                ChildrenMixin.PrecedenceDisplayTypes.LOWER_CASE_LETTERS_TCB.value
            ),
            query="Check the post-natal register for 20 entries done in the last month.",
            question_code="5678",
            question_group=self.question_group1,
        )
        self.question3 = baker.make(
            Question,
            answer_type=Question.AnswerType.INTEGER.value,
            organisation=self.organisation,
            parent=self.question2,
            precedence=1,
            precedence_display_type=None,
            query=(
                "Number of post-natal women on/started modern method of "
                "family planning in the month (out of the 20)?."
            ),
            question_code="91011",
            question_group=self.question_group1,
        )
        self.question4 = baker.make(
            Question,
            answer_type=Question.AnswerType.TEXT_ANSWER.value,
            organisation=self.organisation,
            parent=None,
            precedence=3,
            precedence_display_type=None,
            query=(
                "In which other service areas/units offer FP counselling/commodities "
                "offered? Specify."
            ),
            question_code="1213",
            question_group=self.question_group1,
        )
        self.responses = baker.make(
            QuestionnaireResponses,
            facility=self.facility,
            organisation=self.organisation,
            questionnaire=self.questionnaire,
        )
        self.user = baker.make(get_user_model(), name=fake.name(), organisation=self.organisation)

    def test_answer_for_responses(self) -> None:
        """Test the Question model's `answer_for_response` method."""

        # Create an answer for question 1
        baker.make(
            QuestionAnswer,
            comments="A comment",
            is_not_applicable=False,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": True},
        )

        assert self.question1.answer_for_responses(self.responses)
        assert not self.question2.answer_for_responses(self.responses)
        assert not self.question3.answer_for_responses(self.responses)
        assert not self.question4.answer_for_responses(self.responses)

    def test_children_property(self) -> None:
        """Test the Question model's `children` property."""

        assert self.question1.children.count() == 0
        assert self.question2.children.count() == 1
        assert self.question2.children.first() == self.question3
        assert self.question3.children.count() == 0
        assert self.question4.children.count() == 0

    def test_is_answerable_property(self) -> None:
        """Test the Question model's `is_answerable` property."""

        assert self.question1.is_answerable
        assert self.question3.is_answerable
        assert self.question3.is_answerable
        assert not self.question2.is_answerable

    def test_is_parent_property(self) -> None:
        """Test the Question model's `is_parent` property."""

        assert self.question2.is_parent
        assert not self.question1.is_parent
        assert not self.question3.is_parent
        assert not self.question3.is_parent

    def test_manager_annotate_with_stats_method(self) -> None:
        """Test the Question model manager's `annotate_with_stats` method."""

        # Create answer for question 1 & question 2
        baker.make(
            QuestionAnswer,
            comments="A comment",
            is_not_applicable=False,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": True},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=self.question2,
            questionnaire_response=self.responses,
            response={"content": None},
        )

        qs = Question.objects.annotate_with_stats(self.responses)
        question1 = qs.get(pk=self.question1.pk)
        question2 = qs.get(pk=self.question2.pk)
        question3 = qs.get(pk=self.question3.pk)

        assert qs.count() == 4

        assert not question1.stats_is_parent
        assert question2.stats_is_parent
        assert not question3.stats_is_parent

        assert question1.stats_answer_for_responses_comments == "A comment"
        assert question2.stats_answer_for_responses_comments is None
        assert question3.stats_answer_for_responses_comments is None

        assert not question1.stats_answer_for_responses_is_not_applicable
        assert question2.stats_answer_for_responses_is_not_applicable
        assert not question3.stats_answer_for_responses_is_not_applicable

        assert question1.stats_answer_for_responses_response == {"content": True}
        assert question2.stats_answer_for_responses_response == {"content": None}
        assert question3.stats_answer_for_responses_response is None

    def test_manager_answerable_method(self) -> None:
        """Test the Question model manager's `answerable` method."""

        answerable_questions = [q.pk for q in Question.objects.answerable()]

        assert self.question1.pk in answerable_questions
        assert self.question2.pk not in answerable_questions
        assert self.question3.pk in answerable_questions
        assert self.question4.pk in answerable_questions

    def test_manager_answered_for_responses_method(self) -> None:
        """Test the Question model manager's `answered_for_responses` method."""

        # Create answer for question 1 & question 2
        baker.make(
            QuestionAnswer,
            comments="A comment",
            is_not_applicable=False,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": True},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=self.question2,
            questionnaire_response=self.responses,
            response={"content": None},
        )

        qs = Question.objects.answered_for_responses(self.responses)
        answered_questions = [q.pk for q in qs]

        assert self.question1.pk in answered_questions
        assert self.question2.pk in answered_questions
        assert self.question3.pk not in answered_questions
        assert self.question4.pk not in answered_questions

    def test_manager_by_precedence_method(self) -> None:  # noqa
        """Test the Question model manager's `by_precedence` method."""

        qs = [q.precedence for q in Question.objects.by_precedence()]

        assert qs == [1, 1, 2, 3]

    def test_manager_for_question_method(self) -> None:
        """Test the Question model manager's `for_question` method."""

        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.SELECT_ONE.value,
            metadata={"select_list_options": ["VIA", "HPV"]},
            organisation=self.organisation,
            parent=self.question3,
            precedence=1,
            precedence_display_type=None,
            query="Screening method used.",
            question_code="1415",
            question_group=self.question_group1,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"min_value": 0}},
            organisation=self.organisation,
            parent=question5,
            precedence=1,
            precedence_display_type=None,
            query="Percentage of positive lesions identified.",
            question_code="1617",
            question_group=self.question_group1,
        )

        assert not Question.objects.for_question(self.question1).exists()
        assert not Question.objects.for_question(self.question4).exists()

        assert Question.objects.for_question(self.question2).count() == 3
        assert question5 in Question.objects.for_question(self.question2)
        assert question6 in Question.objects.for_question(self.question2)
        assert self.question3 in Question.objects.for_question(self.question2)

        assert Question.objects.for_question(self.question3).count() == 2
        assert question5 in Question.objects.for_question(self.question3)
        assert question6 in Question.objects.for_question(self.question3)

        assert Question.objects.for_question(question5).count() == 1
        assert question6 in Question.objects.for_question(question5)

    def test_manager_for_question_group_method(self) -> None:
        """Test the Question model manager's `for_question_group` method."""

        question_group2 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 2",
        )
        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.SELECT_ONE.value,
            metadata={"select_list_options": ["VIA", "HPV"]},
            organisation=self.organisation,
            parent=self.question3,
            precedence=1,
            precedence_display_type=None,
            query="Screening method used.",
            question_code="1415",
            question_group=question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"min_value": 0}},
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=None,
            query="Percentage of positive lesions identified.",
            question_code="1617",
            question_group=question_group2,
        )

        assert Question.objects.for_question_group(self.question_group1).count() == 4
        assert Question.objects.for_question_group(question_group2).count() == 2

        assert self.question1 not in Question.objects.for_question_group(question_group2)
        assert self.question2 not in Question.objects.for_question_group(question_group2)
        assert question5 not in Question.objects.for_question_group(self.question_group1)
        assert question6 not in Question.objects.for_question_group(self.question_group1)

    def test_manager_for_questionnaire_method(self) -> None:
        """Test the Question model manager's `for_questionnaire` method."""

        questionnaire = baker.make(
            Questionnaire,
            name="Test Questionnaire 2",
            organisation=self.organisation,
            questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
        )
        question_group2 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=questionnaire,
            title="Test Question Group 2",
        )
        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.SELECT_ONE.value,
            metadata={"select_list_options": ["VIA", "HPV"]},
            organisation=self.organisation,
            parent=self.question3,
            precedence=1,
            precedence_display_type=None,
            query="Screening method used.",
            question_code="1415",
            question_group=question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"min_value": 0}},
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=None,
            query="Percentage of positive lesions identified.",
            question_code="1617",
            question_group=question_group2,
        )

        assert Question.objects.for_questionnaire(self.questionnaire).count() == 4
        assert Question.objects.for_questionnaire(questionnaire).count() == 2

        assert self.question1 not in Question.objects.for_questionnaire(questionnaire)
        assert self.question2 not in Question.objects.for_questionnaire(questionnaire)
        assert question5 not in Question.objects.for_questionnaire(self.questionnaire)
        assert question6 not in Question.objects.for_questionnaire(self.questionnaire)


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

        assert self.question_group.is_complete_for_responses(self.questionnaire_response) is False

    def test_is_not_applicable_for_questionnaire(self):
        assert (
            self.question_group.is_not_applicable_for_responses(self.questionnaire_response)
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
        self.question.answer_for_responses(self.questionnaire_response)
        self.qn_1.is_answered_for_responses(self.questionnaire_response)
        self.parent_qn.is_answered_for_responses(self.questionnaire_response)
        assert (
            self.question_group.is_not_applicable_for_responses(self.questionnaire_response)
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
        self.question_qs.answered_for_responses(self.questionnaire_response)
        self.question_qs.answerable()
        self.question_qs.for_question(self.question)
        self.question_qs.for_question_group(self.question_group)
        self.question_group_qs.for_questionnaire(self.questionnaire)
        self.question_group_qs.parents_only()
        self.question_group_qs.answered_for_responses(self.questionnaire_response)
        self.questionnaire_response_qs.draft()
        self.questionnaire_response_qs.complete()

    def test_managers(self):
        Question.objects.answerable()
        Question.objects.by_precedence()
        Question.objects.for_question(self.question)
        Question.objects.for_question_group(self.question_group)
        Question.objects.answered_for_responses(self.questionnaire_response)
        QuestionGroup.objects.by_precedence()
        QuestionGroup.objects.for_questionnaire(self.questionnaire)
        QuestionGroup.objects.answered_for_responses(self.questionnaire_response)
        QuestionnaireResponses.objects.draft()
        QuestionnaireResponses.objects.complete()
