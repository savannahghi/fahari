from django.urls import path

from .views import (
    ActivityLogView,
    DailySiteUpdatesView,
    FacilitySystemCreateView,
    FacilitySystemDeleteView,
    FacilitySystemTicketCreateView,
    FacilitySystemTicketDeleteView,
    FacilitySystemTicketUpdateView,
    FacilitySystemUpdateView,
    SiteMentorshipView,
    TicketsView,
    TimeSheetsView,
    VersionsView,
    WeeklyProgramUpdatesView,
)

app_name = "ops"
urlpatterns = [
    path("versions", view=VersionsView.as_view(), name="versions"),
    path(
        "version_create",
        view=FacilitySystemCreateView.as_view(),
        name="version_create",
    ),
    path(
        "version_update/<pk>",
        view=FacilitySystemUpdateView.as_view(),
        name="version_update",
    ),
    path(
        "version_delete/<pk>",
        view=FacilitySystemDeleteView.as_view(),
        name="version_delete",
    ),
    path("tickets", view=TicketsView.as_view(), name="tickets"),
    path(
        "ticket_create",
        view=FacilitySystemTicketCreateView.as_view(),
        name="ticket_create",
    ),
    path(
        "ticket_update/<pk>",
        view=FacilitySystemTicketUpdateView.as_view(),
        name="ticket_update",
    ),
    path(
        "ticket_delete/<pk>",
        view=FacilitySystemTicketDeleteView.as_view(),
        name="ticket_delete",
    ),
    path("activity_log", view=ActivityLogView.as_view(), name="activity_log"),
    path("site_mentorship", view=SiteMentorshipView.as_view(), name="site_mentorship"),
    path(
        "daily_site_updates",
        view=DailySiteUpdatesView.as_view(),
        name="daily_site_updates",
    ),
    path(
        "weekly_program_updates",
        view=WeeklyProgramUpdatesView.as_view(),
        name="weekly_program_updates",
    ),
    path("timesheets", view=TimeSheetsView.as_view(), name="timesheets"),
]
