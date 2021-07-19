from django.urls import path

from .views import (
    ActivityLogView,
    DailySiteUpdatesView,
    SiteMentorshipView,
    TicketsView,
    TimeSheetsView,
    VersionsView,
    WeeklyProgramUpdatesView,
)

app_name = "ops"
urlpatterns = [
    path("versions", view=VersionsView.as_view(), name="versions"),
    path("tickets", view=TicketsView.as_view(), name="tickets"),
    path("activity_log", view=ActivityLogView.as_view(), name="activity_log"),
    path("site_mentorship", view=SiteMentorshipView.as_view(), name="site_mentorship"),
    path("daily_site_updates", view=DailySiteUpdatesView.as_view(), name="daily_site_updates"),
    path(
        "weekly_program_updates",
        view=WeeklyProgramUpdatesView.as_view(),
        name="weekly_program_updates",
    ),
    path("timesheets", view=TimeSheetsView.as_view(), name="timesheets"),
]
