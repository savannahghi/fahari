from django.urls import path

from .views import (
    QuestionnaireResponseCreateView,
    QuestionnaireResponsesView,
    QuestionnaireSelectionView,
)

app_name = "sims"
urlpatterns = [
    path(
        "questionnaire_responses_create/<pk>",
        view=QuestionnaireResponseCreateView.as_view(),
        name="questionnaire_responses_create",
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
