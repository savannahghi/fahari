import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from pepfar_mle.common.views import HomeView

pytestmark = pytest.mark.django_db


def test_approved_mixin_approved_user(rf, django_user_model):
    approved_user = baker.make(django_user_model, is_approved=True)
    url = "/"
    request = rf.get(url)
    request.user = approved_user
    view = HomeView()
    view.setup(request)
    view.dispatch(request)  # no error raised


def test_approved_mixin_non_approved_authenticated_user(rf, django_user_model):
    non_approved_user = baker.make(django_user_model, is_approved=False)
    url = "/"
    request = rf.get(url)
    request.user = non_approved_user
    view = HomeView()
    view.setup(request)
    with pytest.raises(PermissionDenied) as e:
        view.dispatch(request)  # no error raised

    assert "PermissionDenied" in str(e)


def test_home_view(user, client):
    client.force_login(user)
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_about_view(user, client):
    client.force_login(user)
    url = reverse("about")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_facility_view(user, client):
    client.force_login(user)
    url = reverse("common:facilities")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_systems_view(user, client):
    client.force_login(user)
    url = reverse("common:systems")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
