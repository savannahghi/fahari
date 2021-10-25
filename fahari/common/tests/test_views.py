import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from fahari.common.models import Facility
from fahari.common.serializers import FacilitySerializer
from fahari.common.views import DRFSerializerExcelIOMixin, HomeView
from fahari.utils.excel_utils import DRFSerializerExcelIO, DRFSerializerExcelIOTemplate

pytestmark = pytest.mark.django_db


def test_approved_mixin_approved_user(rf, user_with_all_permissions):
    approved_user = user_with_all_permissions
    url = "/"
    request = rf.get(url)
    request.user = approved_user
    view = HomeView()
    view.setup(request)
    view.dispatch(request)  # no error raised


def test_approved_mixin_non_approved_authenticated_user(rf, django_user_model):
    non_approved_user = baker.make(django_user_model, email="juha@kalulu.com", is_approved=False)
    url = reverse("common:facilities")
    request = rf.get(url)
    request.user = non_approved_user
    view = HomeView()
    view.setup(request)
    with pytest.raises(PermissionDenied) as e:
        view.dispatch(request)  # no error raised

    assert "PermissionDenied" in str(e)


def test_home_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_about_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("about")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_facility_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("common:facilities")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_systems_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("common:systems")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_user_facility_allotment_view(user_with_all_permissions, client):
    client.force_login(user_with_all_permissions)
    url = reverse("common:user_facility_allotments")
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_drf_excel_io_mixin_get_filter_form(rf, user_with_all_permissions):
    url = reverse("api:facility-dump-data")
    request = rf.get(url)
    request.user = user_with_all_permissions
    response = DRFSerializerExcelIOMixin.as_view(
        {"get": "get_filter_form"},
        excel_io_class=DRFSerializerExcelIO,
        excel_io_template_class=DRFSerializerExcelIOTemplate,
        queryset=Facility.objects.fahari_facilities(),
        serializer_class=FacilitySerializer,
    )(request=request)

    assert response.status_code == status.HTTP_200_OK
