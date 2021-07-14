import pytest
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from model_bakery import baker

from pepfar_mle.common.admin import OrganisationAdmin
from pepfar_mle.common.forms import OrganisationForm
from pepfar_mle.common.models import Organisation

pytestmark = pytest.mark.django_db


@pytest.fixture
def request_with_user(rf, django_user_model):
    url = settings.ADMIN_URL + "/common/organisation/add/"
    request = rf.get(url)
    user = baker.make(django_user_model)
    request.user = user
    return request


@pytest.fixture
def organisation_admin():
    admin = OrganisationAdmin(model=Organisation, admin_site=AdminSite())
    return admin


@pytest.fixture
def organisation_form():
    form = OrganisationForm()
    return form


def test_base_admin_update_created_by(request_with_user, organisation_admin, organisation_form):
    org = baker.prepare(Organisation)
    assert org.created_by is None
    assert org.updated_by is None
    organisation_admin.save_model(request_with_user, org, organisation_form, change=False)
    assert org.created_by is not None
    assert org.updated_by is not None


def test_base_admin_update_updated_by(request_with_user, organisation_admin, organisation_form):
    org = baker.make(Organisation)
    original_created_by = org.created_by
    original_updated_by = org.updated_by

    organisation_admin.save_model(request_with_user, org, organisation_form, change=True)
    assert org.created_by == original_created_by
    assert org.updated_by != original_updated_by
