import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_system_versions_view(user, client):
    client.force_login(user)
    url = reverse("ops:versions")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_tickets_view(user, client):
    client.force_login(user)
    url = reverse("ops:tickets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_activity_log_view(user, client):
    client.force_login(user)
    url = reverse("ops:activity_log")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_site_mentorship_view(user, client):
    client.force_login(user)
    url = reverse("ops:site_mentorship")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_daily_site_updates_view(user, client):
    client.force_login(user)
    url = reverse("ops:daily_site_updates")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_timesheets_view(user, client):
    client.force_login(user)
    url = reverse("ops:timesheets")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
