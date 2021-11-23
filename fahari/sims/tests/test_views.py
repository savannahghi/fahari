import json

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from faker.proxy import Faker
from model_bakery import baker

from fahari.common.models.common_models import Facility
from fahari.common.tests.test_api import LoggedInMixin
from fahari.sims.forms import QuestionnaireResponsesForm
from fahari.sims.models import Questionnaire, QuestionnaireResponses
from fahari.sims.views import (
    MentorshipQuestionnaireResponsesView,
    QuestionnaireResponseCreateView,
    QuestionnaireResponsesCaptureView,
    QuestionnaireResponsesView,
)

fake = Faker()


def test_questionnaire_response_context():
    v = QuestionnaireResponsesView()
    ctx = v.get_context_data()
    assert ctx["active"] == "sims-nav"
    assert ctx["selected"] == "questionnaire-responses"


def test_mentorship_questionnaire_context():
    v = MentorshipQuestionnaireResponsesView()
    v.get_context_data()


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
        view = QuestionnaireResponseCreateView()
        form = QuestionnaireResponsesForm()
        form.cleaned_data = []
        form.mentors = json.dumps(
            [
                {"name": "salad", "email": "abc@yahoo.com", "member_org": "sil", "role": "s.e"},
                {"name": "rosio", "email": "def@yahoo.com", "member_org": "sil", "role": "s.e"},
            ]
        )
        view.form_valid(form)

    def test_get_initial(self):
        request = self.factory.post(
            reverse(
                "sims:questionnaire_responses_create",
                self.questionnaire_response,
                kwargs={"pk": self.questionnaire_response.pk},
            )
        )
        view = QuestionnaireResponseCreateView()
        view.setup(request, pk=self.questionnaire_response.pk)
        # view.get(request)
        init = view.get_initial()
        init["questionnaire"] = self.questionnaire
