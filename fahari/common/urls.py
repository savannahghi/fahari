from django.urls import path

from .views import (
    FacilityCreateView,
    FacilityDeleteView,
    FacilityUpdateView,
    FacilityView,
    SystemCreateView,
    SystemDeleteView,
    SystemsView,
    SystemUpdateView,
)

app_name = "common"
urlpatterns = [
    path("facilities", view=FacilityView.as_view(), name="facilities"),
    path(
        "facility_create",
        view=FacilityCreateView.as_view(),
        name="facility_create",
    ),
    path(
        "facility_update/<pk>",
        view=FacilityUpdateView.as_view(),
        name="facility_update",
    ),
    path(
        "facility_delete/<pk>",
        view=FacilityDeleteView.as_view(),
        name="facility_delete",
    ),
    path("systems", view=SystemsView.as_view(), name="systems"),
    path(
        "system_create",
        view=SystemCreateView.as_view(),
        name="system_create",
    ),
    path(
        "system_update/<pk>",
        view=SystemUpdateView.as_view(),
        name="system_update",
    ),
    path(
        "system_delete/<pk>",
        view=SystemDeleteView.as_view(),
        name="system_delete",
    ),
]
