import json

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from faker.proxy import Faker
from model_bakery import baker

from fahari.common.models.common_models import Facility
from fahari.common.tests.test_api import LoggedInMixin
from fahari.sims.forms import QuestionnaireResponsesForm
from fahari.sims.models import QuestionGroup, Questionnaire, QuestionnaireResponses
from fahari.sims.views import (
    QuestionnaireResponsesCaptureView,
    QuestionnaireResponsesCreateView,
    QuestionnaireResponsesView,
    QuestionnaireResponseUpdateView,
    QuestionnaireSelectionView,
)

fake = Faker()


def test_questionnaire_response_context():
    v = QuestionnaireResponsesView()
    ctx = v.get_context_data()
    assert ctx["active"] == "sims-nav"
    assert ctx["selected"] == "questionnaire-responses"


class TestQuestionnaireResponseCapture(LoggedInMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        org = self.global_organisation
        self.facility = baker.make(Facility, organisation=org, name=fake.text(max_nb_chars=30))
        self.questionnaire = baker.make(
            Questionnaire, name=fake.text(max_nb_chars=30), questionnaire_type="mentorship"
        )
        self.questionnaire_response = baker.make(
            QuestionnaireResponses,
            organisation=org,
            facility=self.facility,
            questionnaire=self.questionnaire,
        )

        self.question_group = baker.make(
            QuestionGroup,
            title=fake.text(max_nb_chars=30),
            questionnaire=self.questionnaire,
            precedence=1,
        )
        super().setUp()

    def test_questionnaire_response_context(self, **kwargs):
        request = self.factory.get(
            reverse(
                "sims:questionnaire_responses_capture",
                kwargs={"pk": self.questionnaire_response.pk},
            )
        )
        view = QuestionnaireResponsesCaptureView()
        view.setup(request, pk=self.questionnaire_response.pk)
        view.get(request)
        ctx = view.get_context_data()
        assert "current_step" in ctx
        assert "questionnaire" in ctx
        assert "total_steps" in ctx

    def test_form_valid(self):
        form = QuestionnaireResponsesForm()
        form.facility = self.facility  # type: ignore
        form.questionnaire = self.questionnaire  # type: ignore
        form.mentors = json.dumps(  # type: ignore
            {"name": "mentor", "email": "abc@yahoo.com", "member_org": "sil", "role": "s.e"}
        )
        form.cleaned_data = []
        form.is_valid()
        # view.form_valid(form)

    def test_get_initial(self):
        pass

    def test_create_questionnaire_response_url(self):
        request = self.factory.post(
            reverse(
                "sims:questionnaire_responses_update",
                None,
                kwargs={"pk": self.questionnaire_response.pk},
            )
        )
        v = QuestionnaireResponsesCreateView()
        v.setup(request, pk=self.questionnaire_response.pk)
        url = "sims/questionnaire_responses"
        assert url in v.get_success_url()

    def test_questionnaire_response_update(self):
        request = self.factory.post(
            reverse(
                "sims:questionnaire_responses_update",
                None,
                kwargs={"pk": self.questionnaire_response.pk},
            )
        )
        v = QuestionnaireResponseUpdateView()
        v.setup(request, pk=self.questionnaire_response.pk)
        v.get(request, pk=self.questionnaire_response.pk)
        v.get_context_data()

    def test_questionnaire_selection_context_data(self):
        v = QuestionnaireSelectionView()
        ctx = v.get_context_data()
        assert "questionnaires" in ctx
