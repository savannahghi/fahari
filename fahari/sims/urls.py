from django.urls import path

from .views import (
    QuestionnaireResponsesCaptureView,
    QuestionnaireResponsesCreateView,
    QuestionnaireResponsesUpdateView,
    QuestionnaireResponsesView,
    QuestionnaireSelectionView,
)

app_name = "sims"
urlpatterns = [
    path(
        "questionnaire_responses_capture/<pk>",
        view=QuestionnaireResponsesCaptureView.as_view(),
        name="questionnaire_responses_capture",
    ),
    path(
        "questionnaire_responses_create/<pk>",
        view=QuestionnaireResponsesCreateView.as_view(),
        name="questionnaire_responses_create",
    ),
    path(
        "questionnaire_responses_update/<pk>",
        view=QuestionnaireResponsesUpdateView.as_view(),
        name="questionnaire_responses_update",
    ),
    path(
        "questionnaire_responses",
        view=QuestionnaireResponsesView.as_view(),
        name="questionnaire_responses",
    ),
    path(
        "questionnaire_selection",
        view=QuestionnaireSelectionView.as_view(),
        name="questionnaire_selection",
    ),
]
