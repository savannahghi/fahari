import json
import uuid

from django.urls import reverse
from faker import Faker
from model_bakery import baker

from fahari.common.models import Facility
from fahari.common.tests.test_api import LoggedInMixin
from fahari.sims.models import (
    ChildrenMixin,
    Question,
    QuestionAnswer,
    QuestionGroup,
    Questionnaire,
    QuestionnaireResponses,
)

fake = Faker()


class QuestionnaireResponsesViewSetTest(LoggedInMixin):
    def setUp(self):
        super().setUp()
        self.facility = baker.make(
            Facility,
            county="Kajiado",
            organisation=self.global_organisation,
            sub_county="Kajiado East",
        )
        self.questionnaire = baker.make(
            Questionnaire,
            name="Test Questionnaire 1",
            organisation=self.global_organisation,
            questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
        )
        self.question_group1 = baker.make(
            QuestionGroup,
            organisation=self.global_organisation,
            parent=None,
            precedence=1,
            precedence_display_type=ChildrenMixin.PrecedenceDisplayTypes.NUMBERED_TD.value,
            questionnaire=self.questionnaire,
            title="Test Question Group 1",
        )
        self.question1 = baker.make(
            Question,
            answer_type=Question.AnswerType.YES_NO.value,
            organisation=self.global_organisation,
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
            organisation=self.global_organisation,
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
            organisation=self.global_organisation,
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
            organisation=self.global_organisation,
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
            organisation=self.global_organisation,
            questionnaire=self.questionnaire,
        )

    def test_create(self) -> None:
        data = {
            "facility": self.facility.pk,
            "organisation": self.global_organisation.pk,
            "questionnaire": self.questionnaire.pk,
        }
        response = self.client.post(reverse("api:questionnaireresponses-list"), data=data)

        assert response.status_code == 201

    def test_mark_question_group_as_applicable(self) -> None:
        # Start by marking all the questions as non applicable.
        question_answer_data = {"is_not_applicable": True, "response": {"content": None}}
        for question in Question.objects.for_question_group(self.question_group1):
            QuestionAnswer.objects.update_or_create(
                organisation=question.organisation,
                question=question,
                questionnaire_response=self.responses,
                defaults=question_answer_data,
            )
        assert self.question_group1.is_not_applicable_for_responses(self.responses)

        data = {"question_group": self.question_group1.pk}
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-mark-question-group-as-applicable",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
        )

        assert response.status_code == 200
        assert not self.question_group1.is_not_applicable_for_responses(self.responses)
        assert (
            not Question.objects.for_question_group(self.question_group1)
            .annotate_with_stats(self.responses)
            .filter(stats_answer_for_responses_is_not_applicable=True)
            .exists()
        )

    def test_mark_question_group_as_applicable_with_invalid_payload(self) -> None:
        data = {"question_group": uuid.uuid4()}  # A non existing pk as payload
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-mark-question-group-as-applicable",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
        )

        assert response.status_code == 400

    def test_mark_question_group_as_non_applicable(self) -> None:
        data = {"question_group": self.question_group1.pk}
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-mark-question-group-as-non-applicable",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
        )

        assert response.status_code == 200
        assert self.question_group1.is_not_applicable_for_responses(self.responses)

    def test_mark_question_group_as_non_applicable_with_invalid_payload(self) -> None:
        data = {"question_group": uuid.uuid4()}  # A non existing pk as payload
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-mark-question-group-as-non-applicable",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
        )

        assert response.status_code == 400

    def test_retrieve(self) -> None:
        response = self.client.get(reverse("api:questionnaireresponses-list"), draft=True)

        assert response.status_code == 200, response.json()
        assert response.data["count"] >= 1, response.json()  # noqa

    def test_patch(self) -> None:
        data = {"active": False}
        response = self.client.patch(
            reverse("api:questionnaireresponses-detail", kwargs={"pk": self.responses.pk}), data
        )

        assert response.status_code == 200, response.json()
        assert not response.data["active"]  # noqa

    def test_put(self) -> None:
        data = {
            "active": False,
            "facility": self.facility.pk,
            "organisation": self.global_organisation.pk,
            "questionnaire": self.questionnaire.pk,
        }
        response = self.client.patch(
            reverse("api:questionnaireresponses-detail", kwargs={"pk": self.responses.pk}), data
        )

        assert response.status_code == 200, response.json()
        assert not response.data["active"]  # noqa

    def test_save_question_group_answers(self) -> None:
        data = {
            "question_group": self.question_group1.pk,
            "question_answers": {
                str(self.question1.pk): {"comments": "A comment.", "response": True},
                str(self.question4.pk): {"comments": None, "response": "A response."},
            },
        }
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-save-question-group-answers",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
            format="json",
        )

        assert response.status_code == 200
        assert self.question1.is_answered_for_responses(self.responses)
        assert self.question4.is_answered_for_responses(self.responses)
        assert not self.question2.is_answered_for_responses(self.responses)
        assert not self.question3.is_answered_for_responses(self.responses)

        assert self.question1.answer_for_responses(self.responses).comments == "A comment."
        assert self.question1.answer_for_responses(self.responses).response["content"]

    def test_save_question_group_answers_with_invalid_question_pk(self) -> None:
        invalid_pk = uuid.uuid4()
        data = {
            "question_group": self.question_group1.pk,
            "question_answers": {
                # A random pk
                str(invalid_pk): {"comments": "A comment.", "response": True},
                str(self.question4.pk): {"comments": None, "response": "A response."},
            },
        }
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-save-question-group-answers",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
            format="json",
        )

        assert response.status_code == 400, response.json()
        assert response.data["error_message"] == (  # noqa
            'A question with id "%s" does not exist.' % str(invalid_pk)
        )

    def test_save_question_group_answers_with_invalid_question_group_pk(self) -> None:
        data = {
            "question_group": str(uuid.uuid4()),  # An invalid pk
            "question_answers": {
                str(self.question1.pk): {"comments": "A comment.", "response": True},
                str(self.question4.pk): {"comments": None, "response": "A response."},
            },
        }
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-save-question-group-answers",
                kwargs={"pk": self.responses.pk},
            ),
            data=data,
            format="json",
        )

        assert response.status_code == 400, response.json()
        assert response.data["error_message"] == (  # noqa
            'A question group with id "%s" does not exist.' % data["question_group"]
        )

    def test_submit_questionnaire_responses(self) -> None:
        response = self.client.post(
            reverse(
                "api:questionnaireresponses-submit-questionnaire-responses",
                kwargs={"pk": self.responses.pk},
            ),
            data={},
            format="json",
        )
        self.responses.refresh_from_db()

        assert response.status_code == 302
        assert self.responses.is_complete
        assert self.responses.finish_date is not None

    def test_questionnaireresponse_create_view(self):
        data = {
            "organisation": self.global_organisation.pk,
            "facility": self.facility.pk,
            "questionnaire": self.questionnaire.pk,
            "mentors": json.dumps(
                [
                    {
                        "name": fake.name(),
                        "phone": "0754987654",
                        "email": fake.email(),
                        "member_org": fake.name(),
                    }
                ],
            ),
        }
        req = self.client.post(
            reverse("sims:questionnaire_responses_create", kwargs={"pk": self.questionnaire.pk}),
            data,
        )
        assert req.status_code == 302

    def test_questionnaireresponse_update_view(self):
        data = {
            "organisation": self.global_organisation.pk,
            "facility": self.facility.pk,
            "questionnaire": self.questionnaire.pk,
            "mentors": json.dumps(
                [
                    {
                        "name": fake.name(),
                        "email": fake.email(),
                        "member_org": fake.name(),
                    }
                ],
            ),
        }
        response = self.client.post(
            reverse("sims:questionnaire_responses_update", kwargs={"pk": self.responses.pk}), data
        )
        assert response.status_code == 302
