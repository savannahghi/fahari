import pytest
from django.core.exceptions import PermissionDenied
from model_bakery import baker

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
