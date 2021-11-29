import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility, Organisation
from fahari.sims.models import (
    ChildrenMixin,
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
        Questionnaire,
        QuestionAnswer,
        QuestionnaireResponses,
    ]
    for model in models:
        instance = baker.prepare(model)
        assert str(instance) != ""


class _CommonTestCase(TestCase):
    """Common tests setup for the models in the sims app."""

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


class QuestionTest(_CommonTestCase):
    """Tests for the Question model."""

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

        assert not question1.stats_is_parent  # type: ignore
        assert question2.stats_is_parent  # type: ignore
        assert not question3.stats_is_parent  # type: ignore

        assert question1.stats_answer_for_responses_comments == "A comment"  # type: ignore
        assert question2.stats_answer_for_responses_comments is None  # type: ignore
        assert question3.stats_answer_for_responses_comments is None  # type: ignore

        assert not question1.stats_answer_for_responses_is_not_applicable  # type: ignore
        assert question2.stats_answer_for_responses_is_not_applicable  # type: ignore
        assert not question3.stats_answer_for_responses_is_not_applicable  # type: ignore

        assert question1.stats_answer_for_responses_response == {"content": True}  # type: ignore
        assert question2.stats_answer_for_responses_response == {"content": None}  # type: ignore
        assert question3.stats_answer_for_responses_response is None  # type: ignore

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

    def test_representation(self) -> None:
        """Test the Question's model's `__str__` method."""

        assert str(self.question1) == self.question1.query
        assert str(self.question2) == self.question2.query
        assert str(self.question3) == self.question3.query
        assert str(self.question4) == self.question4.query


class QuestionGroupTest(_CommonTestCase):
    """Tests for the QuestionGroup model."""

    def setUp(self) -> None:
        super().setUp()
        self.question_group2 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=2,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 2",
        )
        self.question_group3 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=self.question_group2,
            precedence=1,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 3",
        )
        self.question_group4 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=3,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 4",
        )

    def test_children_property(self) -> None:
        """Test the QuestionGroup model's `children` property."""

        assert self.question_group1.children.count() == 0
        assert self.question_group2.children.count() == 1
        assert self.question_group2.children.first() == self.question_group3
        assert self.question_group3.children.count() == 0
        assert self.question_group4.children.count() == 0

    def test_direct_decedents_only_property(self) -> None:
        """Test the QuestionGroup model's `direct_decedents_only` property."""

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
            question_group=self.question_group2,
        )

        assert self.question_group1.direct_decedents_only.count() == 3
        assert self.question_group2.direct_decedents_only.count() == 0
        assert self.question_group3.direct_decedents_only.count() == 0
        assert self.question_group4.direct_decedents_only.count() == 0
        assert self.question_group3 not in self.question_group1.direct_decedents_only
        assert question5 not in self.question_group1.direct_decedents_only

    def test_is_answerable_property(self) -> None:
        """Test the QuestionGroup's model's `is_answerable` property."""

        baker.make(
            Question,
            answer_type=Question.AnswerType.SELECT_ONE.value,
            metadata={"select_list_options": ["VIA", "HPV"]},
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=None,
            query="Screening method used.",
            question_code="1415",
            question_group=self.question_group2,
        )

        assert self.question_group1.is_answerable
        assert self.question_group2.is_answerable
        assert not self.question_group3.is_answerable
        assert not self.question_group4.is_answerable

    def test_is_parent_property(self) -> None:
        """Test the QuestionGroup's model's `is_parent` property."""

        assert self.question_group2.is_parent
        assert not self.question_group1.is_parent
        assert not self.question_group3.is_parent
        assert not self.question_group3.is_parent

    def test_is_complete_for_responses(self) -> None:
        """Test the QuestionGroup's model's `is_complete_for_responses` method."""

        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"ratio_upper_bound": 20}},
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=(
                ChildrenMixin.PrecedenceDisplayTypes.LOWER_CASE_LETTERS_TCB.value
            ),
            query=(
                "Check at least 20 HEI in cohorts. Proportion that is "
                "correctly filled and up to date.",
            ),
            question_code="1415",
            question_group=self.question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"depends_on": "1415", "constraints": {"dependency_type": "numerator"}},
            organisation=self.organisation,
            parent=question5,
            precedence=1,
            precedence_display_type=None,
            query="6 weeks- was DBS done and result documented?",
            question_code="1617",
            question_group=self.question_group2,
        )

        # Answer some of the questions
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
        baker.make(
            QuestionAnswer,
            comments="A comment",
            is_not_applicable=False,
            organisation=self.organisation,
            question=question5,
            questionnaire_response=self.responses,
            response={"content": [15, 20]},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=question6,
            questionnaire_response=self.responses,
            response={"content": [4, 20]},
        )

        assert not self.question_group1.is_complete_for_responses(self.responses)
        assert self.question_group3.is_complete_for_responses(self.responses)
        assert self.question_group4.is_complete_for_responses(self.responses)
        assert self.question_group2.is_complete_for_responses(self.responses)

    def test_is_not_applicable_for_responses(self) -> None:
        """Test the QuestionGroup's model's `is_not_applicable_for_responses` method."""

        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"ratio_upper_bound": 20}},
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=(
                ChildrenMixin.PrecedenceDisplayTypes.LOWER_CASE_LETTERS_TCB.value
            ),
            query=(
                "Check at least 20 HEI in cohorts. Proportion that is "
                "correctly filled and up to date.",
            ),
            question_code="1415",
            question_group=self.question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"depends_on": "1415", "constraints": {"dependency_type": "numerator"}},
            organisation=self.organisation,
            parent=question5,
            precedence=1,
            precedence_display_type=None,
            query="6 weeks- was DBS done and result documented?",
            question_code="1617",
            question_group=self.question_group2,
        )

        # Answer some of the questions
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": None},
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
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=question5,
            questionnaire_response=self.responses,
            response={"content": None},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=question6,
            questionnaire_response=self.responses,
            response={"content": None},
        )

        assert not self.question_group1.is_not_applicable_for_responses(self.responses)
        assert not self.question_group3.is_not_applicable_for_responses(self.responses)
        assert not self.question_group4.is_not_applicable_for_responses(self.responses)
        assert self.question_group2.is_not_applicable_for_responses(self.responses)

    def test_manager_annotate_with_stats_method(self) -> None:
        """Test the QuestionGroup's model manager's `annotate_with_stats` method."""

        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"ratio_upper_bound": 20}},
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=(
                ChildrenMixin.PrecedenceDisplayTypes.LOWER_CASE_LETTERS_TCB.value
            ),
            query=(
                "Check at least 20 HEI in cohorts. Proportion that is "
                "correctly filled and up to date.",
            ),
            question_code="1415",
            question_group=self.question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"depends_on": "1415", "constraints": {"dependency_type": "numerator"}},
            organisation=self.organisation,
            parent=question5,
            precedence=1,
            precedence_display_type=None,
            query="6 weeks- was DBS done and result documented?",
            question_code="1617",
            question_group=self.question_group2,
        )

        # Answer some of the questions
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": None},
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
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=question5,
            questionnaire_response=self.responses,
            response={"content": None},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=question6,
            questionnaire_response=self.responses,
            response={"content": None},
        )

        qs = QuestionGroup.objects.annotate_with_stats(self.responses)
        question_group1 = qs.get(pk=self.question_group1.pk)
        question_group2 = qs.get(pk=self.question_group2.pk)
        question_group3 = qs.get(pk=self.question_group3.pk)
        question_group4 = qs.get(pk=self.question_group4.pk)

        assert qs.count() == 4

        assert not question_group1.stats_is_parent  # type: ignore
        assert not question_group3.stats_is_parent  # type: ignore
        assert not question_group4.stats_is_parent  # type: ignore
        assert question_group2.stats_is_parent  # type: ignore

        assert question_group1.stats_is_answerable  # type: ignore
        assert question_group2.stats_is_answerable  # type: ignore
        assert not question_group3.stats_is_answerable  # type: ignore
        assert not question_group4.stats_is_answerable  # type: ignore

        assert not question_group1.stats_is_complete_for_responses  # type: ignore
        assert question_group2.stats_is_complete_for_responses  # type: ignore
        assert question_group3.stats_is_complete_for_responses  # type: ignore
        assert question_group4.stats_is_complete_for_responses  # type: ignore

        assert not question_group1.stats_is_not_applicable_for_responses  # type: ignore
        assert not question_group3.stats_is_not_applicable_for_responses  # type: ignore
        assert not question_group4.stats_is_not_applicable_for_responses  # type: ignore
        assert question_group2.stats_is_not_applicable_for_responses  # type: ignore

    def test_manager_answered_for_responses_method(self) -> None:
        """Test the QuestionGroup's model manager's `annotate_answered_for_responses` method."""

        question5 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"constraints": {"ratio_upper_bound": 20}},
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=(
                ChildrenMixin.PrecedenceDisplayTypes.LOWER_CASE_LETTERS_TCB.value
            ),
            query=(
                "Check at least 20 HEI in cohorts. Proportion that is "
                "correctly filled and up to date.",
            ),
            question_code="1415",
            question_group=self.question_group2,
        )
        question6 = baker.make(
            Question,
            answer_type=Question.AnswerType.FRACTION.value,
            metadata={"depends_on": "1415", "constraints": {"dependency_type": "numerator"}},
            organisation=self.organisation,
            parent=question5,
            precedence=1,
            precedence_display_type=None,
            query="6 weeks- was DBS done and result documented?",
            question_code="1617",
            question_group=self.question_group2,
        )

        # Answer some of the questions
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=self.question1,
            questionnaire_response=self.responses,
            response={"content": None},
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
        baker.make(
            QuestionAnswer,
            comments="N/A",
            is_not_applicable=True,
            organisation=self.organisation,
            question=question5,
            questionnaire_response=self.responses,
            response={"content": None},
        )
        baker.make(
            QuestionAnswer,
            comments=None,
            is_not_applicable=True,
            organisation=self.organisation,
            question=question6,
            questionnaire_response=self.responses,
            response={"content": None},
        )

        qs = QuestionGroup.objects.answered_for_responses(self.responses)

        assert self.question_group1 in qs
        assert self.question_group2 in qs
        assert self.question_group3 not in qs
        assert self.question_group4 not in qs

    def test_manager_by_precedence_method(self) -> None:  # noqa
        """Test the QuestionGroup's model manager's `by_precedence` method."""

        qs = [q.precedence for q in QuestionGroup.objects.by_precedence()]

        assert qs == [1, 1, 2, 3]

    def test_manager_for_questionnaire_method(self) -> None:
        """Test the QuestionGroup's model manager's `for_questionnaire` method."""

        questionnaire = baker.make(
            Questionnaire,
            name="Test Questionnaire 2",
            organisation=self.organisation,
            questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
        )
        question_group5 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=None,
            precedence=1,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=questionnaire,
            title="Test Question Group 5",
        )
        question_group6 = baker.make(
            QuestionGroup,
            organisation=self.organisation,
            parent=question_group5,
            precedence=1,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=questionnaire,
            title="Test Question Group 6",
        )

        assert QuestionGroup.objects.for_questionnaire(self.questionnaire).count() == 4
        assert QuestionGroup.objects.for_questionnaire(questionnaire).count() == 2

        assert question_group5 not in QuestionGroup.objects.for_questionnaire(self.questionnaire)
        assert question_group6 not in QuestionGroup.objects.for_questionnaire(self.questionnaire)

        assert self.question_group1 not in QuestionGroup.objects.for_questionnaire(questionnaire)
        assert self.question_group2 not in QuestionGroup.objects.for_questionnaire(questionnaire)
        assert self.question_group3 not in QuestionGroup.objects.for_questionnaire(questionnaire)
        assert self.question_group4 not in QuestionGroup.objects.for_questionnaire(questionnaire)

    def test_representation(self) -> None:
        """Test the QuestionGroup's model's `__str__` method."""

        assert str(self.question_group1) == self.question_group1.title
        assert str(self.question_group2) == self.question_group2.title
        assert str(self.question_group3) == self.question_group3.title
        assert str(self.question_group4) == self.question_group4.title
