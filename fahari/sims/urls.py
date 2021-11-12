from django.urls import path

from .views import QuestionnaireResponsesView, QuestionnaireSelectionView

app_name = "sims"
urlpatterns = [
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
