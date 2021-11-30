import json

import pytest
from django.test import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from faker.proxy import Faker
from model_bakery import baker
from rest_framework import status

from fahari.common.models.common_models import Facility
from fahari.common.models.organisation_models import Organisation
from fahari.common.tests.test_api import LoggedInMixin
from fahari.sims.models import Questionnaire, QuestionnaireResponses
from fahari.sims.views import (
    QuestionnaireResponsesCaptureView,
    QuestionnaireResponsesCreateView,
    QuestionnaireResponsesView,
    QuestionnaireResponseUpdateView,
)

pytestmark = pytest.mark.django_db


fake = Faker()


def test_questionnaire_response_capture(user_with_all_permissions, client):
    organisation = baker.make(Organisation)
    facility = baker.make(Facility, organisation=organisation, name=fake.name())
    questionnaire = baker.make(
        Questionnaire,
        organisation=organisation,
        name=fake.name(),
        questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
    )

    responses = baker.make(
        QuestionnaireResponses,
        facility=facility,
        organisation=organisation,
        questionnaire=questionnaire,
    )
    client.force_login(user_with_all_permissions)
    url = reverse("sims:questionnaire_responses_capture", kwargs={"pk": responses.pk})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_questionnaire_response_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("sims:questionnaire_responses")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_questionnaire_response_list(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("api:questionnaireresponses-list")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_questionnaire_questionnaire_selection(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("sims:questionnaire_selection")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_questionnaireresponse_context_data():
    view = QuestionnaireResponsesView()
    ctx = view.get_context_data()
    assert ctx["active"] == "sims-nav"
    assert ctx["selected"] == "questionnaire-responses"


class TestMultipleViews(LoggedInMixin, TestCase):
    def setUp(self):
        org = baker.make(Organisation)
        self.facility = baker.make(
            Facility,
            county="Kajiado",
            organisation=org,
            sub_county="Kajiado East",
        )
        self.questionnaire = baker.make(
            Questionnaire,
            name="Test Questionnaire 1",
            organisation=org,
            questionnaire_type=Questionnaire.QuestionnaireTypes.MENTORSHIP.value,
        )
        self.response = baker.make(
            QuestionnaireResponses,
            facility=self.facility,
            organisation=org,
            questionnaire=self.questionnaire,
        )
        super().setUp()

    def test_questionnaire_response_capture_context_data(self, **kwargs):
        request = RequestFactory().get(
            reverse("sims:questionnaire_responses_capture", kwargs={"pk": self.response.pk}),
        )
        request.user = self.user
        view = QuestionnaireResponsesCaptureView()
        view.setup(request, pk=self.response.pk)
        view.dispatch(request, pk=self.response.pk)
        ctx = view.get_context_data()
        self.assertEqual(ctx["current_step"], 2)
        self.assertEqual(ctx["questionnaire"], self.questionnaire)
        self.assertEqual(ctx["questionnaire_is_complete"], self.response.is_complete)
        self.assertEqual(ctx["total_steps"], 2)

    def test_questionnaire_response_create_get_context_data(self, **kwargs):
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
                        "phone": "0777889900",
                    }
                ],
            ),
        }

        request = RequestFactory().post(
            reverse("sims:questionnaire_responses_create", kwargs={"pk": self.questionnaire.pk}),
            data,
        )
        request.user = self.user
        view = QuestionnaireResponsesCreateView()
        view.setup(request, pk=self.questionnaire.pk)
        view.dispatch(request, pk=self.questionnaire.pk)
        ctx = view.get_context_data()
        assert ctx["current_step"] == 1
        self.assertIn("mentor_details_form", ctx)
        assert ctx["questionnaire"] == self.questionnaire
        assert ctx["total_steps"] == 2

    def test_questionnaire_response_update_get_context_data(self):
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

        request = RequestFactory().post(
            reverse("sims:questionnaire_responses_update", kwargs={"pk": self.response.pk}), data
        )
        request.user = self.user
        view = QuestionnaireResponseUpdateView()
        view.setup(request, pk=self.response.pk)
        view.dispatch(request, pk=self.response.pk)
        ctx = view.get_context_data()
        assert ctx["current_step"] == 1
        self.assertIn("mentor_details_form", ctx)
        assert ctx["questionnaire"] == self.questionnaire
        assert ctx["total_steps"] == 2
