import pytest
from django.urls import reverse
from rest_framework import status

from fahari.ops.views import FacilitySystemsView, FacilitySystemTicketsView

pytestmark = pytest.mark.django_db


def test_system_versions_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:versions")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_tickets_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:tickets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_activity_log_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:activity_log")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_site_mentorship_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:site_mentorship")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_daily_site_updates_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:daily_site_updates")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_timesheets_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:timesheets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_weekly_program_updates_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("ops:weekly_program_updates")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_version_context_data():
    v = FacilitySystemsView()
    ctx = v.get_context_data()
    assert ctx["active"] == "program-nav"
    assert ctx["selected"] == "versions"


def test_tickets_context_data():
    v = FacilitySystemTicketsView()
    ctx = v.get_context_data()
    assert ctx["active"] == "program-nav"
    assert ctx["selected"] == "tickets"
